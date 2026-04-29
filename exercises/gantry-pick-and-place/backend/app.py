"""
Gantry Pick & Place Backend Application

Entry point for the FastAPI backend using vention-communication and vention-state-machine.

Run with: uvicorn app:app --reload
"""

# from fastapi import FastAPI
import asyncio
from typing import Optional
from communication.app import VentionApp
from communication.decorators import action, stream
from pydantic import BaseModel

from models.runtime import Position, RuntimeModel, runtime_state
from state_machine_impl import my_state_machine, Triggers


class StatusResponse(BaseModel):
    """Status response model for API responses."""
    robot_position: Position
    home_position: Position
    cube_start_position: Position
    destination_position: Position
    gripper_state: str
    state_machine_state: str
    is_moving: bool
    error: Optional[str] = None


def _runtime_to_status() -> StatusResponse:
    """Convert runtime state to status response."""
    state = runtime_state.get_state()
    return StatusResponse(
        robot_position=state.robot_position,
        home_position=state.home_position,
        cube_start_position=state.cube_start_position,
        destination_position=state.destination_position,
        gripper_state=state.gripper_state.value,
        state_machine_state=state.state_machine_state,
        is_moving=state.is_moving,
        error=state.error,
    )


# Create the VentionApp instance
app = VentionApp(name="GantryPickAndPlace", emit_proto=True)


# ============================================================================
# RPC Actions
# ============================================================================

@action()
async def get_status() -> StatusResponse:
    """Get current robot and state machine status."""
    return _runtime_to_status()


@action()
async def home_robot() -> StatusResponse:
    """Trigger the home operation."""
    print("Triggering home operation")
    my_state_machine.trigger(Triggers.to_home.name)
    return _runtime_to_status()


@action()
async def start_sequence() -> StatusResponse:
    """Start the pick-and-place sequence. Must be in home state."""
    print("Starting pick-and-place sequence")
    if runtime_state.get_state().state_machine_state != "Running_home":
        return StatusResponse(
            robot_position=runtime_state.get_state().robot_position,
            home_position=runtime_state.get_state().home_position,
            cube_start_position=runtime_state.get_state().cube_start_position,
            destination_position=runtime_state.get_state().destination_position,
            gripper_state=runtime_state.get_state().gripper_state.value,
            state_machine_state=runtime_state.get_state().state_machine_state,
            is_moving=runtime_state.get_state().is_moving,
            error="Sequence can only start from home state",
        )
    my_state_machine.trigger(Triggers.to_move_to_cube.name)
    return _runtime_to_status()


@action()
async def set_cube_position(position: Position) -> StatusResponse:
    """Set the cube start position."""
    runtime_state.update(cube_start_position=position)
    return _runtime_to_status()


@action()
async def set_destination_position(position: Position) -> StatusResponse:
    """Set the destination position."""
    runtime_state.update(destination_position=position)
    return _runtime_to_status()


@action()
async def get_cube_position() -> Position:
    """Get the cube start position."""
    return runtime_state.get_state().cube_start_position


@action()
async def get_destination_position() -> Position:
    """Get the destination position."""
    return runtime_state.get_state().destination_position


# ============================================================================
# Streams
# ============================================================================

@stream(name="status", payload=StatusResponse, replay=False, queue_maxsize=100, policy="fifo")
async def status_stream() -> StatusResponse:
    """Stream live status updates."""
    print("Emitting status update")
    return _runtime_to_status()

async def loop():
    while True:
        asyncio.create_task(status_stream())
        await asyncio.sleep(0.1)  # Update every 100 ms for smooth live updates
# ============================================================================
# Startup / Shutdown
# ============================================================================

@app.on_event("startup")
async def startup():
    """Initialize the state machine on app startup."""
    my_state_machine.start()
    print("State machine started, ready to accept commands.")
    asyncio.create_task(loop())


# Finalize the app to register routes and emit proto
app.finalize()

# # Expose the FastAPI app for uvicorn
# fastapi_app = app

print("Gantry Pick & Place backend is running...")