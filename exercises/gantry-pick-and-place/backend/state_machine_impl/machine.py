"""
Pick-and-place state machine implementation for the Gantry backend.

This state machine is implemented using the vention-state-machine package.
"""

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

    async def _move_to(self, target: Position, speed: int = 90) -> Optional[str]:
        _, _, error = await self.controller.poll_move_to(target, speed=speed)
        return error

    @on_state_change
    def on_state_change(self, old_state, new_state, trigger_name):
        self._update_state(state_name=new_state, is_moving=False)

    @on_enter_state(States.running.home)
    async def enter_home(self, _):
        print("Entering home state, moving robot to home position")
        self._update_state(state_name="Running_home", is_moving=True)
        error = await self.controller.home()
        if error and error[2]:
            self._update_state(state_name="Running_home", is_moving=False, error=error[2])
            return
        print("Robot homed successfully")

        # TODO: This is a bit of a hack to automatically transition to the next state after transition completes.
        # TODO: call this trigger externally from the API after transition is complete instead of automatically transitioning here.
        # print("Transitioning to moveToCube")
        # self.trigger(Triggers.to_move_to_cube.name)

    @on_enter_state(States.running.moveToCube)
    async def enter_move_to_cube(self, _):
        print("Entering moveToCube state, moving robot above cube start position")
        self._update_state(state_name="moveToCube", is_moving=True)
        cube_pos = self._current_cube_position()
        target = Position(x=cube_pos.x, y=cube_pos.y, z=SAFE_TRAVEL_Z)
        error = await self._move_to(target)
        if error:
            self._update_state(state_name="moveToCube", is_moving=False, error=error)
            return
        print("Robot moved above cube successfully")
        
        # TODO: This is a bit of a hack to automatically transition to the next state after transition completes.
        # TODO: call this trigger externally from the API after transition is complete instead of automatically transitioning here.
        print("Transitioning to lowerToPick")
        self.trigger(Triggers.to_lower_to_pick.name)

    @on_enter_state(States.running.lowerToPick)
    async def enter_lower_to_pick(self, _):
        print("Entering lowerToPick state, lowering robot to cube to pick")
        self._update_state(state_name="lowerToPick", is_moving=True)
        cube_pos = self._current_cube_position()
        current = self._current_robot_position()
        target = Position(x=current.x, y=current.y, z=cube_pos.z)
        error = await self._move_to(target)
        if error:
            self._update_state(state_name="lowerToPick", is_moving=False, error=error)
            return
        print("Robot lowered to cube successfully")
        
        # TODO: This is a bit of a hack to automatically transition to the next state after transition completes.
        # TODO: call this trigger externally from the API after transition is complete instead of automatically transitioning here.
        print("Transitioning to closeGripper")
        self.trigger(Triggers.to_close_gripper.name)

    @on_enter_state(States.running.closeGripper)
    def enter_close_gripper(self, _):
        print("Entering closeGripper state, closing gripper to pick cube")
        self._update_state(state_name="closeGripper", is_moving=False)
        self.controller.close_gripper()
        print("Gripper closed successfully")
        
        # TODO: This is a bit of a hack to automatically transition to the next state after transition completes.
        # TODO: call this trigger externally from the API after transition is complete instead of automatically transitioning here.
        print("Transitioning to liftCube")
        self.trigger(Triggers.to_lift_cube.name)

    @on_enter_state(States.running.liftCube)
    async def enter_lift_cube(self, _):
        print("Entering liftCube state, lifting cube up to safe travel height")
        self._update_state(state_name="liftCube", is_moving=True)
        current = self._current_robot_position()
        target = Position(x=current.x, y=current.y, z=SAFE_TRAVEL_Z)
        error = await self._move_to(target)
        if error:
            self._update_state(state_name="liftCube", is_moving=False, error=error)
            return
        print("Cube lifted successfully")
        
        # TODO: This is a bit of a hack to automatically transition to the next state after transition completes.
        # TODO: call this trigger externally from the API after transition is complete instead of automatically transitioning here.
        print("Transitioning to moveToDest")
        self.trigger(Triggers.to_move_to_dest.name)

    @on_enter_state(States.running.moveToDest)
    async def enter_move_to_dest(self, _):
        print("Entering moveToDest state, moving robot to destination position")
        self._update_state(state_name="moveToDest", is_moving=True)
        dest = self._current_destination_position()
        target = Position(x=dest.x, y=dest.y, z=SAFE_TRAVEL_Z)
        error = await self._move_to(target)
        if error:
            self._update_state(state_name="moveToDest", is_moving=False, error=error)
            return
        print("Robot moved to destination successfully")
        
        # TODO: This is a bit of a hack to automatically transition to the next state after transition completes.
        # TODO: call this trigger externally from the API after transition is complete instead of automatically transitioning here.
        print("Transitioning to lowerToPlace")
        self.trigger(Triggers.to_lower_to_place.name)

    @on_enter_state(States.running.lowerToPlace)
    async def enter_lower_to_place(self, _):
        print("Entering lowerToPlace state, lowering robot to destination position")
        self._update_state(state_name="lowerToPlace", is_moving=True)
        dest = self._current_destination_position()
        current = self._current_robot_position()
        target = Position(x=dest.x, y=dest.y, z=dest.z)
        error = await self._move_to(target)
        if error:
            self._update_state(state_name="lowerToPlace", is_moving=False, error=error)
            return
        print("Robot lowered to destination successfully")
        
        # TODO: This is a bit of a hack to automatically transition to the next state after transition completes.
        # TODO: call this trigger externally from the API after transition is complete instead of automatically transitioning here.
        print("Transitioning to openGripper")
        self.trigger(Triggers.to_open_gripper.name)

    @on_enter_state(States.running.openGripper)
    def enter_open_gripper(self, _):
        print("Entering openGripper state, opening gripper to place cube")
        self._update_state(state_name="openGripper", is_moving=False)
        self.controller.open_gripper()
        print("Gripper opened successfully")
        
        # TODO: This is a bit of a hack to automatically transition to the next state after transition completes.
        # TODO: call this trigger externally from the API after transition is complete instead of automatically transitioning here.
        print("Transitioning to liftFromPlace")
        self.trigger(Triggers.to_lift_from_place.name)

    @on_enter_state(States.running.liftFromPlace)
    async def enter_lift_from_place(self, _):
        print("Entering liftFromPlace state, lifting cube from destination position")
        self._update_state(state_name="liftFromPlace", is_moving=True)
        dest = self._current_destination_position()
        target = Position(x=dest.x, y=dest.y, z=SAFE_TRAVEL_Z)
        error = await self._move_to(target)
        if error:
            self._update_state(state_name="liftFromPlace", is_moving=False, error=error)
            return
        print("Cube lifted from destination successfully")
        
        # TODO: This is a bit of a hack to automatically transition to the next state after transition completes.
        # TODO: call this trigger externally from the API after transition is complete instead of automatically transitioning here.
        print("Transitioning to complete")
        self.trigger(Triggers.to_complete.name)

    @on_enter_state(States.running.complete)
    def enter_complete(self, _):
        print("Entering complete state, sequence complete")
        self._update_state(state_name="complete", is_moving=False)


my_state_machine = GantryStateMachine()
