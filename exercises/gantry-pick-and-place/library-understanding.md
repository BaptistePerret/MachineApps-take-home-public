# Library Understanding: `vention-communication` and `vention-state-machine`

This document explains the purpose, features, and usage of the two required libraries for the gantry pick-and-place project. Use this as a reference when implementing the backend.

---

## 1. `vention-communication` (v0.4.1)

### Purpose
`vention-communication` is a **FastAPI-based RPC framework** that bridges machine-app developers and frontend clients by turning annotated Python functions into typed network endpoints automatically. No manual REST/gRPC boilerplate required.

### Key Problem It Solves
Machine-app developers write Python but shouldn't need to know REST, gRPC, or complex networking. This library exposes async Python functions as network APIs with a single decorator.

### Core Features

#### 1. **Actions** (Request-Response)
- One-request, one-response pattern
- Input/output types inferred from Python annotations
- Use `@action()` decorator

```python
from pydantic import BaseModel
from communication.app import VentionApp
from communication.decorators import action

class StatusRequest(BaseModel):
    ok: bool

@action()
async def get_status() -> StatusRequest:
    return StatusRequest(ok=True)
```

#### 2. **Streams** (Server-Streaming)
- Continuous, live data broadcast to subscribers
- Perfect for telemetry (robot position, state, gripper status)
- Configurable replay behavior and queue policy
- Use `@stream()` decorator

```python
from communication.decorators import stream

@stream(name="robot_status", payload=RobotStatus, replay=True, queue_maxsize=1, policy="latest")
async def robot_status_stream():
    return RobotStatus(position=[x, y, z], gripper_open=False)
```

#### 3. **Proto Generation**
- Automatically generates `.proto` schema files at runtime
- Enables SDK generation for TypeScript, Python, Go via Buf
- Results in **auto-completed frontend methods** with strong typing

#### 4. **Connect-Compatible Transport**
- Works with `@connectrpc/connect-web` (TypeScript/React)
- Works with `connectrpc-python` (Python clients)
- All methods mounted under `/rpc/<service>/<method>` routes

### Installation
```bash
pip install vention-communication
```

Requires: Python 3.10+, FastAPI, Uvicorn

### Basic Usage Pattern for Gantry Project

```python
from communication.app import VentionApp
from communication.decorators import action, stream
from pydantic import BaseModel

# Define models
class RobotStatus(BaseModel):
    position: list[float]  # [x, y, z]
    gripper_open: bool
    state: str  # current state machine state
    error: str | None = None

# Create app
app = VentionApp(name="GantryApp", emit_proto=True)

# Define actions for commands
@action()
async def home_robot() -> RobotStatus:
    # Trigger home state machine event
    return current_status()

@action()
async def start_sequence() -> RobotStatus:
    # Trigger start state machine event
    return current_status()

# Define streams for telemetry
@stream(name="status", payload=RobotStatus, replay=True, queue_maxsize=1, policy="latest")
async def status_stream():
    # Published continuously; frontend subscribes
    return get_current_status()

# Finalize and run
app.finalize()
# uvicorn main:app
```

### Key Takeaways for Gantry
- Use **`@action()`** for command endpoints: `Home Robot`, `Start Sequence`, `Set Cube Position`, etc.
- Use **`@stream()`** for live telemetry: robot position, gripper state, current state-machine state.
- The frontend automatically gets typed RPC methods; no manual HTTP client code needed.
- Call `app.finalize()` before serving the app.

---

## 2. `vention-state-machine` (v0.4.7)

### Purpose
`vention-state-machine` is a **declarative state machine framework** for machine apps. It simplifies building async-safe, recoverable hierarchical state machines with minimal boilerplate.

### Why It's Needed for Gantry
The pick-and-place sequence is inherently **stateful**: idle → move to cube → lower → close gripper → lift → move to destination → lower → open gripper → lift → complete. The library makes orchestrating these transitions clean and maintainable.

### Core Concepts

#### 1. **States & StateGroups**
- States are leaf nodes (e.g., `idle`, `picking`, `placing`)
- StateGroups organize related states hierarchically
- All machines include built-in `ready` and `fault` states

```python
from state_machine.defs import StateGroup, State

class Running(StateGroup):
    move_to_cube: State = State()
    lower_to_pick: State = State()
    close_gripper: State = State()
    lift_cube: State = State()
    move_to_dest: State = State()
    lower_to_place: State = State()
    open_gripper: State = State()
    lift_from_place: State = State()

class States:
    running = Running()
    idle: State = State()
```

#### 2. **Triggers**
- Named events that initiate transitions
- Examples: `start`, `move_complete`, `error_detected`, `reset`

```python
from state_machine.defs import Trigger

class Triggers:
    start = Trigger("start")
    motion_complete = Trigger("motion_complete")
    gripper_closed = Trigger("gripper_closed")
    to_fault = Trigger("to_fault")
    reset = Trigger("reset")
```

#### 3. **Transitions**
- Declarative list defining which state transitions are allowed
- Format: `Trigger.transition(from_state, to_state)`

```python
TRANSITIONS = [
    Triggers.start.transition("ready", States.running.move_to_cube),
    Triggers.motion_complete.transition(States.running.move_to_cube, States.running.lower_to_pick),
    Triggers.gripper_closed.transition(States.running.close_gripper, States.running.lift_cube),
    # ... more transitions
]
```

#### 4. **Callbacks / Decorators**
- `@on_enter_state(state)` — runs when entering a state (where motion logic goes)
- `@on_exit_state(state)` — runs when leaving a state
- `@auto_timeout(seconds, trigger)` — auto-trigger if state timeout expires
- `@guard(trigger)` — blocks transition if condition fails
- `@on_state_change` — global callback on any transition

```python
from state_machine.core import StateMachine
from state_machine.decorators import on_enter_state, auto_timeout

class PickAndPlaceMachine(StateMachine):
    def __init__(self, robot):
        super().__init__(states=States, transitions=TRANSITIONS)
        self.robot = robot
    
    @on_enter_state(States.running.moveToCube)
    def enter_move_to_cube(self, _):
        # Start moving to cube position
        self.robot.move_to(self.cubPosition)
    
    @on_enter_state(States.running.lowerToPick)
    def enter_lower_to_pick(self, _):
        # Lower Z axis to pick the cube
        self.robot.move_to([self.robot.x, self.robot.y, pick_z])
    
    @on_enter_state(States.running.closeGripper)
    def enter_close_gripper(self, _):
        # Close the gripper
        self.robot.closed_gripper()
        self.trigger(Triggers.gripper_closed.value)
```

#### 5. **Built-in Features**
- **State Recovery**: `enable_last_state_recovery=True` allows resuming from last state on restart
- **History Tracking**: Full transition history with timestamps and durations
- **Async Task Spawning**: `spawn(coroutine)` for background motion tasks
- **Global Callbacks**: `@on_state_change` for logging, MQTT publish, etc.

#### 6. **RPC Integration**
- **Integrate with `vention-communication`**: Use `build_state_machine_bundle()` to expose state machine via RPC
- Automatically creates RPC actions: `GetState`, `GetHistory`, `Trigger_<TriggerName>`

```python
from state_machine.vention_communication import build_state_machine_bundle

state_machine = PickAndPlaceMachine(robot)
state_machine.start()

app = VentionApp(name="GantryApp")
bundle = build_state_machine_bundle(state_machine)
app.register_rpc_plugin(bundle)
app.finalize()
```

### Installation
```bash
pip install vention-state-machine
```

Optional: `vention-communication` for RPC integration, `graphviz` for state diagrams

### Key Methods
- `state_machine.start()` — enter the machine (or recover from last state)
- `state_machine.trigger(trigger_name)` — manually trigger a transition
- `state_machine.state` — get current state
- `state_machine.history` — get full transition history

---

## Integration Pattern: Gantry Pick-and-Place

### How They Work Together

1. **State Machine** (`vention-state-machine`) orchestrates the pick-and-place logic
   - Defines states and transitions
   - On state entry, calls `robot.move_to()` repeatedly until motion completes
   - Triggers transitions when motion is done

2. **Communication** (`vention-communication`) exposes the machine to the frontend
   - `@action()` for `home_robot()`, `start_sequence()`, `set_cube_position()`
   - `@stream()` for live robot position, gripper state, current state
   - Frontend polls or subscribes to telemetry

3. **Data Flow**
   ```
   Frontend 
      ↓
   vention-communication RPC call (e.g., /rpc/.../StartSequence)
      ↓
   Backend action handler triggers state machine
      ↓
   State machine enters state, runs callback
      ↓
   Callback calls robot.move_to() in a loop until complete
      ↓
   State machine publishes telemetry via @stream()
      ↓
   Frontend receives telemetry update via subscription
   ```

### Architecture Overview

```
┌─────────────────────────────────────────────────┐
│          React + TypeScript Frontend            │
│  (polls or subscribes to robot_status stream)   │
└────────────────┬────────────────────────────────┘
                 │
                 │ /rpc/.../StartSequence
                 ↓
┌─────────────────────────────────────────────────┐
│       FastAPI + vention-communication            │
│  - @action() for Home, Start, Set commands      │
│  - @stream() for telemetry broadcast            │
└────────────────┬────────────────────────────────┘
                 │
                 │ Calls state_machine.trigger()
                 ↓
┌─────────────────────────────────────────────────┐
│    vention-state-machine (Pick-and-Place FSM)    │
│  - States: idle, move_to_cube, lower, ... etc   │
│  - Callbacks: @on_enter_state() loop move_to()  │
│  - Triggers motion completion transitions       │
└────────────────┬────────────────────────────────┘
                 │
                 │ Calls robot.move_to() loop
                 ↓
┌─────────────────────────────────────────────────┐
│          Robot Simulator (robot_sim.py)          │
│  - move_to() for XYZ motion                      │
│  - closed_gripper() / open_gripper()             │
└─────────────────────────────────────────────────┘
```

---

## Implementation Checklist

### For `vention-communication`:
- [ ] Create `VentionApp` instance with `emit_proto=True`
- [ ] Define Pydantic models for all request/response types
- [ ] Create `@action()` methods for commands (home, start, set position)
- [ ] Create `@stream()` method for telemetry broadcast
- [ ] Call `app.register_rpc_plugin(bundle)` if integrating state machine
- [ ] Call `app.finalize()` before running uvicorn

### For `vention-state-machine`:
- [ ] Define `StateGroup` for running states and top-level idle state
- [ ] Define `Triggers` for all transitions
- [ ] Create `TRANSITIONS` list declaratively
- [ ] Subclass `StateMachine` and implement `@on_enter_state()` callbacks
- [ ] In callbacks, repeatedly call `robot.move_to()` until motion completes
- [ ] Call `state_machine.start()` on app startup
- [ ] Call `state_machine.trigger()` from action handlers

### Integration:
- [ ] Build state machine RPC bundle with `build_state_machine_bundle()`
- [ ] Register bundle with `app.register_rpc_plugin(bundle)`
- [ ] Finalize app and test endpoints with frontend

---

## References
- `vention-communication`: https://pypi.org/project/vention-communication/
- `vention-state-machine`: https://pypi.org/project/vention-state-machine/
- Project README: `exercises/gantry-pick-and-place/README.md`
- Simulator: `exercises/gantry-pick-and-place/backend/robot_sim.py`
