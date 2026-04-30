"""
Shared runtime model for the Gantry Pick & Place backend.

This module defines the runtime state used by the state machine and API.
"""

from enum import Enum
from threading import Lock
from typing import Optional

from pydantic import BaseModel, Field


class Position(BaseModel):
    x: float = Field(0.0, description="X coordinate in millimeters")
    y: float = Field(0.0, description="Y coordinate in millimeters")
    z: float = Field(0.0, description="Z coordinate in millimeters")


class GripperState(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class RuntimeModel(BaseModel):
    robot_position: Position = Position()
    home_position: Position = Position()
    cube_start_position: Position = Position()
    destination_position: Position = Position()
    gripper_state: GripperState = GripperState.OPEN
    state_machine_state: str = "ready"
    is_moving: bool = False
    error: Optional[str] = None

    class Config:
        orm_mode = True


class SharedRuntimeState:
    """Thread-safe runtime state container."""

    def __init__(self) -> None:
        self._lock = Lock()
        self.state = RuntimeModel()

    def get_state(self) -> RuntimeModel:
        with self._lock:
            return self.state.model_copy(deep=True)

    def update(self, **kwargs) -> RuntimeModel:
        with self._lock:
            self.state = self.state.model_copy(update=kwargs)
            updated_state = self.state.model_copy(deep=True)
            return updated_state


runtime_state = SharedRuntimeState()
