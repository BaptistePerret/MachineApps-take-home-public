"""
High-level robot wrapper for the Gantry Pick & Place backend.

This module adapts the low-level simulator interface in robot_sim.py into a backend-friendly
controller that updates shared runtime state and exposes higher-level actions.
"""

import time
from threading import Lock
from typing import Optional, Sequence, Union

from models.runtime import GripperState, Position, runtime_state
from robot_sim import GripperState as SimGripperState, Robot


PositionInput = Union[Position, Sequence[float]]


class RobotController:
    """High-level robot controller that wraps the simulator and runtime state."""

    def __init__(self, robot: Optional[Robot] = None) -> None:
        self._robot = robot or Robot()
        self._lock = Lock()
        self._sync_runtime()

    @staticmethod
    def _to_position(value: PositionInput) -> Position:
        if isinstance(value, Position):
            return value
        if len(value) != 3:
            raise ValueError("Position must be three numeric values: [x, y, z].")
        return Position(x=float(value[0]), y=float(value[1]), z=float(value[2]))

    @staticmethod
    def _to_list(value: PositionInput) -> list[float]:
        if isinstance(value, Position):
            return [value.x, value.y, value.z]
        if len(value) != 3:
            raise ValueError("Position must be three numeric values: [x, y, z].")
        return [float(value[0]), float(value[1]), float(value[2])]

    @staticmethod
    def _to_runtime_gripper_state(value: SimGripperState) -> GripperState:
        return GripperState.OPEN if value == SimGripperState.OPEN else GripperState.CLOSED

    def _sync_runtime(self, error: Optional[str] = None) -> None:
        robot_pos = Position(
            x=self._robot.current_position[0],
            y=self._robot.current_position[1],
            z=self._robot.current_position[2],
        )
        runtime_state.update(
            robot_position=robot_pos,
            home_position=Position(
                x=self._robot.home_position[0],
                y=self._robot.home_position[1],
                z=self._robot.home_position[2],
            ),
            gripper_state=self._to_runtime_gripper_state(self._robot.gripper_state),
            is_moving=any(abs(v) > 0 for v in self._robot.axis_speed),
            error=error,
        )
        print(f"Robot position: x={robot_pos.x:.2f}, y={robot_pos.y:.2f}, z={robot_pos.z:.2f}")

    def get_runtime_state(self):
        return runtime_state.get_state()

    def poll_move_to(
        self,
        target_position: PositionInput,
        speed: int = 90,
        poll_interval: float = 0.05,
    ) -> tuple[Position, list[float], Optional[str]]:
        target_list = self._to_list(target_position)

        with self._lock:
            while True:
                position, axis_speed, error = self._robot.move_to(target_list, speed)
                self._sync_runtime(error=error)
                if error:
                    return self._to_position(position), axis_speed, error
                if axis_speed == [0, 0, 0]:
                    break
                time.sleep(poll_interval)

            return self._to_position(self._robot.current_position), axis_speed, None

    def home(self, speed: int = 50) -> tuple[Position, list[float], Optional[str]]:
        return self.poll_move_to(self._robot.home_position, speed=speed)

    def set_home_position(self, value: PositionInput) -> Position:
        position = self._to_position(value)
        self._robot.home_position = self._to_list(position)
        runtime_state.update(home_position=position)
        return position

    def set_cube_start_position(self, value: PositionInput) -> Position:
        position = self._to_position(value)
        runtime_state.update(cube_start_position=position)
        return position

    def set_destination_position(self, value: PositionInput) -> Position:
        position = self._to_position(value)
        runtime_state.update(destination_position=position)
        return position

    def set_robot_position(self, value: PositionInput) -> Position:
        position = self._to_position(value)
        self._robot.current_position = self._to_list(position)
        self._sync_runtime()
        return position

    def close_gripper(self) -> GripperState:
        self._robot.closed_gripper()
        self._sync_runtime()
        return self.get_runtime_state().gripper_state

    def open_gripper(self) -> GripperState:
        self._robot.open_gripper()
        self._sync_runtime()
        return self.get_runtime_state().gripper_state


robot_controller = RobotController()
