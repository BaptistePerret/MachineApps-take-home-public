## Plan: Gantry Pick & Place Implementation

This document is the working plan and implementation tracker for the `gantry-pick-and-place` exercise. It is intended to be shared with other VS Code chats and used as the primary source of project context.

### Purpose
- Implement a Python backend using `FastAPI`, `vention-state-machine`, and the provided `robot_sim.py` simulator.
- Implement a React + TypeScript frontend that displays live telemetry and allows control of the robot sequence.
- Focus on the mandatory requirements in the exercise README.

---

## Project scope
### Mandatory backend requirements
- Use `vention-communication` for frontend/backend communication.
- Use `vention-state-machine` to orchestrate robot motion and gripper actions.
- Interface with `exercises/gantry-pick-and-place/backend/robot_sim.py`.
- Implement the full Pick-and-Place sequence.
- Provide API endpoints for: get/set robot, cube, and destination positions; `Home Robot`; `Start Sequence`; `Get Status`.

### Mandatory frontend requirements
- Dashboard showing:
  - Current robot position (X, Y, Z)
  - Cube start position
  - Destination position
  - Gripper state
  - Current state-machine state
- Controls for:
  - Cube/destination coordinate configuration
  - Home operation
  - Start sequence
- Visual indication of errors and operational state.

---

## Current repository status
- Backend folder exists: `exercises/gantry-pick-and-place/backend`
- Simulator file exists: `exercises/gantry-pick-and-place/backend/robot_sim.py`
- No frontend app exists currently in the exercise folder.
- Requirements are defined in `exercises/gantry-pick-and-place/backend/requirements.txt`.

---

## Implementation plan
### 1. Backend setup
Tasks:
- [x] Create application entry point in `exercises/gantry-pick-and-place/backend` (e.g. `app.py` or `main.py`).
- [x] Add module structure for API, state machine, and shared models.
- [x] Confirm `requirements.txt` includes `fastapi`, `uvicorn`, `vention-state-machine`, and `vention-storage`.
- [x] Add a `start` command or dev instruction for `uvicorn`.

Notes:
- `robot_sim.py` does not currently import `vention-communication`, but the backend can wrap the simulator and expose REST endpoints.
- `move_to` is time-based and returns partial progress; the backend must repeatedly call it until the motion is complete.

### 2. Backend state and flow
Tasks:
- [x] Define a shared runtime model with:
  - `robot_position`
  - `home_position`
  - `cube_start_position`
  - `destination_position`
  - `gripper_state`
  - `state_machine_state`
  - `is_moving` flag
- [x] Create a wrapper around `Robot` from `robot_sim.py`.
- [x] Create a state machine with the following states:
  - `idle`
  - `home`
  - `move_to_cube`
  - `lower_to_pick`
  - `close_gripper`
  - `lift_cube`
  - `move_to_dest`
  - `lower_to_place`
  - `open_gripper`
  - `lift_from_place`
  - `complete`
- [x] Implement callbacks for each state.
- [x] For motion states, call `robot.move_to(target_position, speed)` repeatedly until `axis_speed == [0,0,0]` or the motion completes.

Design notes:
- Use a single state machine instance in memory.
- Keep robot coordinates and gripper state in a thread-safe or request-safe container if using async endpoints.
- Keep state transitions deterministic and clearly logged.

### 3. Backend API endpoints
Tasks:
- [x] `GET /api/status` — returns robot position, cube position, destination, gripper state, current state, moving status, and any error.
- [x] `POST /api/robot/home` — triggers homing.
- [x] `POST /api/robot/start` — triggers the pick-and-place sequence.
- [x] `GET /api/config/cube` — get cube start coordinates.
- [x] `POST /api/config/cube` — set cube start coordinates.
- [x] `GET /api/config/destination` — get destination coordinates.
- [x] `POST /api/config/destination` — set destination coordinates.

Design notes:
- Use Pydantic models for all request/response bodies.
- Keep endpoint names consistent and intuitive.
- Keep state/status calls lightweight and query-friendly.

### 4. Pick-and-place sequence logic
Tasks:
- [ ] Home operation:
  - call `robot.move_home(speed=50)`
  - poll until motion completes
- [ ] Pick operation:
  - move to cube XY at safe Z height
  - lower to pick height (cube Z)
  - close gripper
  - lift to travel height
- [ ] Place operation:
  - move to destination XY at travel height
  - lower to place height
  - open gripper
  - lift back to travel height
- [ ] Mark sequence completion and return to `idle` or `complete` state.

Design notes:
- Use numeric values for safe heights: e.g. travel Z above cube/placement, pick Z at target height.
- Keep the same speed settings for predictable motion.
- Ensure the backend does not transition before `move_to` returns completed position.

### 5. Frontend structure and dashboard
Tasks:
- [ ] Create `exercises/gantry-pick-and-place/frontend` with React + TypeScript app.
- [ ] Add UI components:
  - `RobotTelemetryCard`
  - `PositionConfigurationForm`
  - `CommandButtons`
  - `StateDisplay`
  - `ErrorBanner`
- [ ] Implement polling or polling interval to refresh `/api/status` every 500–1000 ms.
- [ ] Implement commands for `Home` and `Start Sequence`.
- [ ] Implement coordinate forms for cube start and destination.
- [ ] Add operational/error visuals: success, warning, busy, error.

Design notes:
- A simple polling model is acceptable; websockets are optional.
- Keep frontend UI minimal but clear.
- Surface current state-machine state prominently.

### 6. Validation and testing
Tasks:
- [ ] Manually test backend state transitions from `idle` to `complete`.
- [ ] Test `Home` command separately.
- [ ] Test coordinate updates and status refresh.
- [ ] Test the full pick-and-place sequence end-to-end.
- [ ] Optionally add unit tests for:
  - state machine callback logic
  - `robot_sim.py` motion control wrapper
  - API endpoint validation

Optional bonus tasks:
- [ ] Persist cube/destination configuration using `vention-storage`.
- [ ] Add a Docker Compose stack with frontend/backend.

---

## Details for future implementation chats
When starting a new chat, include:
- Current repo path: `exercises/gantry-pick-and-place`
- Existing backend files in the following folder : `backend/`
- No frontend currently exists under this exercise.
- Use this plan file as the canonical source for required features and task sequencing.
- Highlight that the backend must poll `robot.move_to(...)` repeatedly until motion completes in each state.

Use these tags/phrases to keep context consistent:
- `state machine` / `pick and place sequence`
- `robot_sim.py` / `move_to polling`
- `FastAPI backend` / `React TypeScript frontend`
- `robot position`, `cube position`, `destination position`, `gripper state`, `current state`

---

## Status tracker
- [x] Backend app entry point created
- [x] State machine module created
- [x] API schema models created
- [x] REST endpoints created (RPC actions via vention-communication)
- [ ] Pick-and-place sequence implemented
- [ ] React frontend created
- [ ] Telemetry dashboard implemented
- [ ] Controls implemented
- [ ] Manual end-to-end validation completed
- [ ] Optional persistence / storage added
- [ ] Optional tests added

---

## Relevant file references
- `exercises/gantry-pick-and-place/backend/robot_sim.py`
- `exercises/gantry-pick-and-place/backend/requirements.txt`
- `exercises/gantry-pick-and-place/README.md`
- `exercises/gantry-pick-and-place/frontend/` (to create)
