"""
Pick-and-place state machine implementation for the Gantry backend.

This state machine is implemented using the vention-state-machine package.
"""
import asyncio
from typing import Optional

from state_machine.core import StateMachine
from state_machine.defs import State, StateGroup, Trigger
from state_machine.decorators import on_enter_state, on_state_change

from robot_controller import RobotController, robot_controller
from models.runtime import Position, runtime_state


SAFE_TRAVEL_Z = 200.0


class Running(StateGroup):
    home: State = State()
    moveToCube: State = State()
    lowerToPick: State = State()
    closeGripper: State = State()
    liftCube: State = State()
    moveToDest: State = State()
    lowerToPlace: State = State()
    openGripper: State = State()
    liftFromPlace: State = State()
    complete: State = State()

class States:
    running = Running()

class Triggers:
    start = Trigger("start")
    reset = Trigger("reset")
    to_home = Trigger("to_home")
    to_move_to_cube = Trigger("to_move_to_cube")
    to_lower_to_pick = Trigger("to_lower_to_pick")
    to_close_gripper = Trigger("to_close_gripper")
    to_lift_cube = Trigger("to_lift_cube")
    to_move_to_dest = Trigger("to_move_to_dest")
    to_lower_to_place = Trigger("to_lower_to_place")
    to_open_gripper = Trigger("to_open_gripper")
    to_lift_from_place = Trigger("to_lift_from_place")
    to_complete = Trigger("to_complete")
    to_fault = Trigger("to_fault")


TRANSITIONS = [
    Triggers.start.transition("ready", States.running.home),
    Triggers.to_move_to_cube.transition(States.running.home, States.running.moveToCube),
    Triggers.to_lower_to_pick.transition(States.running.moveToCube, States.running.lowerToPick),
    Triggers.to_close_gripper.transition(States.running.lowerToPick, States.running.closeGripper),
    Triggers.to_lift_cube.transition(States.running.closeGripper, States.running.liftCube),
    Triggers.to_move_to_dest.transition(States.running.liftCube, States.running.moveToDest),
    Triggers.to_lower_to_place.transition(States.running.moveToDest, States.running.lowerToPlace),
    Triggers.to_open_gripper.transition(States.running.lowerToPlace, States.running.openGripper),
    Triggers.to_lift_from_place.transition(States.running.openGripper, States.running.liftFromPlace),
    Triggers.to_complete.transition(States.running.liftFromPlace, States.running.complete),
    Triggers.to_home.transition(States.running.complete, States.running.home),
]


class GantryStateMachine(StateMachine):
    def __init__(self, controller: RobotController = robot_controller) -> None:
        self.controller = controller
        super().__init__(states=States, transitions=TRANSITIONS)

    def _update_state(self, state_name: str, is_moving: bool = False, error: Optional[str] = None) -> None:
        runtime_state.update(
            state_machine_state=state_name,
            is_moving=is_moving,
            error=error,
        )

    def _current_cube_position(self) -> Position:
        return runtime_state.get_state().cube_start_position

    def _current_destination_position(self) -> Position:
        return runtime_state.get_state().destination_position

    def _current_robot_position(self) -> Position:
        return runtime_state.get_state().robot_position

    def _current_state_name(self) -> str:
        """Get the current state name for error reporting."""
        return f"Running_{self.current_state.__class__.__name__}" if self.current_state else "unknown"

    async def _move_to_and_trigger_next(self, target: Position, speed: int = 90, next_trigger: str = None):
        """Move to target and trigger next state if specified."""
        _, _, error = await self.controller.poll_move_to(target, speed=speed)
        if error:
            self._update_state(state_name=self._current_state_name(), is_moving=False, error=error)
            return
        print(f"Robot moved successfully to {target}")
        
        if next_trigger:
            print(f"Transitioning to {next_trigger}")
            self.trigger(next_trigger)

    @on_state_change
    def on_state_change(self, old_state, new_state, trigger_name):
        self._update_state(state_name=new_state, is_moving=False)

    @on_enter_state(States.running.home)
    def enter_home(self, _):
        print("Entering home state, moving robot to home position")
        self._update_state(state_name="Running_home", is_moving=True)
        # Start the movement in a background task
        asyncio.create_task(self._move_to_and_trigger_next(
            self.controller._robot.home_position, 
            speed=50
            # No next trigger for home - it stays in home state
        ))

    @on_enter_state(States.running.moveToCube)
    def enter_move_to_cube(self, _):
        print("Entering moveToCube state, moving robot above cube start position")
        self._update_state(state_name="Running_moveToCube", is_moving=True)
        cube_pos = self._current_cube_position()
        target = Position(x=cube_pos.x, y=cube_pos.y, z=SAFE_TRAVEL_Z)
        # Start the movement in a background task
        asyncio.create_task(self._move_to_and_trigger_next(
            target, 
            speed=90, 
            next_trigger=Triggers.to_lower_to_pick.name
        ))

    @on_enter_state(States.running.lowerToPick)
    def enter_lower_to_pick(self, _):
        print("Entering lowerToPick state, lowering robot to cube to pick")
        self._update_state(state_name="Running_lowerToPick", is_moving=True)
        cube_pos = self._current_cube_position()
        current = self._current_robot_position()
        target = Position(x=current.x, y=current.y, z=cube_pos.z)
        # Start the movement in a background task
        asyncio.create_task(self._move_to_and_trigger_next(
            target, 
            speed=90, 
            next_trigger=Triggers.to_close_gripper.name
        ))

    @on_enter_state(States.running.closeGripper)
    def enter_close_gripper(self, _):
        print("Entering closeGripper state, closing gripper to pick cube")
        self._update_state(state_name="Running_closeGripper", is_moving=False)
        self.controller.close_gripper()
        print("Gripper closed successfully")
        
        # TODO: This is a bit of a hack to automatically transition to the next state after transition completes.
        # TODO: call this trigger externally from the API after transition is complete instead of automatically transitioning here.
        print("Transitioning to liftCube")
        self.trigger(Triggers.to_lift_cube.name)

    @on_enter_state(States.running.liftCube)
    def enter_lift_cube(self, _):
        print("Entering liftCube state, lifting cube up to safe travel height")
        self._update_state(state_name="Running_liftCube", is_moving=True)
        current = self._current_robot_position()
        target = Position(x=current.x, y=current.y, z=SAFE_TRAVEL_Z)
        # Start the movement in a background task
        asyncio.create_task(self._move_to_and_trigger_next(
            target, 
            speed=90, 
            next_trigger=Triggers.to_move_to_dest.name
        ))

    @on_enter_state(States.running.moveToDest)
    def enter_move_to_dest(self, _):
        print("Entering moveToDest state, moving robot to destination position")
        self._update_state(state_name="Running_moveToDest", is_moving=True)
        dest = self._current_destination_position()
        target = Position(x=dest.x, y=dest.y, z=SAFE_TRAVEL_Z)
        # Start the movement in a background task
        asyncio.create_task(self._move_to_and_trigger_next(
            target, 
            speed=90, 
            next_trigger=Triggers.to_lower_to_place.name
        ))

    @on_enter_state(States.running.lowerToPlace)
    def enter_lower_to_place(self, _):
        print("Entering lowerToPlace state, lowering robot to destination position")
        self._update_state(state_name="Running_lowerToPlace", is_moving=True)
        dest = self._current_destination_position()
        current = self._current_robot_position()
        target = Position(x=dest.x, y=dest.y, z=dest.z)
        # Start the movement in a background task
        asyncio.create_task(self._move_to_and_trigger_next(
            target, 
            speed=90, 
            next_trigger=Triggers.to_open_gripper.name
        ))

    @on_enter_state(States.running.openGripper)
    def enter_open_gripper(self, _):
        print("Entering openGripper state, opening gripper to place cube")
        self._update_state(state_name="Running_openGripper", is_moving=False)
        self.controller.open_gripper()
        print("Gripper opened successfully")
        
        # TODO: This is a bit of a hack to automatically transition to the next state after transition completes.
        # TODO: call this trigger externally from the API after transition is complete instead of automatically transitioning here.
        print("Transitioning to liftFromPlace")
        self.trigger(Triggers.to_lift_from_place.name)

    @on_enter_state(States.running.liftFromPlace)
    def enter_lift_from_place(self, _):
        print("Entering liftFromPlace state, lifting cube from destination position")
        self._update_state(state_name="Running_liftFromPlace", is_moving=True)
        dest = self._current_destination_position()
        target = Position(x=dest.x, y=dest.y, z=SAFE_TRAVEL_Z)
        # Start the movement in a background task
        asyncio.create_task(self._move_to_and_trigger_next(
            target, 
            speed=90, 
            next_trigger=Triggers.to_complete.name
        ))

    @on_enter_state(States.running.complete)
    def enter_complete(self, _):
        print("Entering complete state, sequence complete")
        self._update_state(state_name="Running_complete", is_moving=False)


my_state_machine = GantryStateMachine()
