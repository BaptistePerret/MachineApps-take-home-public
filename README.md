# MachineApps Take-Home Exercises

## Application Documentation: Gantry Pick & Place

This repository contains a proof-of-concept gantry robot pick-and-place simulation with a Python backend and a React frontend. The application is designed to control a simulated 3-axis gantry robot using a state machine, expose a live telemetry stream, and allow the user to configure cube and destination positions.

> Due to a constrained professional and personal schedule, this implementation reflects approximately 8 hours of focused development effort.

---

## Setup and Run Instructions

The application is fully containerized using Docker Compose. Use the following commands from the exercise root:

```bash
cd exercises/gantry-pick-and-place
docker compose build
docker compose up
```

After the stack starts:

- Backend API and stream endpoint: `http://localhost:8000`
- Frontend dashboard: `http://localhost:3000`

To stop the application, press `Ctrl+C` in the terminal running Compose or use:

```bash
docker compose down
```

If you need to rebuild after making code changes:

```bash
docker compose build --no-cache
```

---

## Architecture Overview

The application is separated into two services:

1. **Backend**: Python FastAPI service using `vention-communication`, `vention-state-machine`, and a simulated robot model.
2. **Frontend**: React + TypeScript dashboard using ConnectRPC to interact with the backend.

### Backend Architecture

- `backend/app.py`
  - Creates a `VentionApp` instance and exports RPC actions for commands, position updates, and status.
  - Starts a background loop that emits status updates every 100ms via a `status` stream.
  - Exposes actions: `get_status`, `home_robot`, `start_sequence`, `set_cube_position`, `set_destination_position`, `get_cube_position`, `get_destination_position`.

- `backend/robot_controller.py`
  - Wraps the simulator `Robot` class and keeps runtime state synchronized.
  - Implements `poll_move_to()` to repeatedly call `robot.move_to()` until motion completes, as required by the simulation.
  - Provides high-level operations: home, move, open/close gripper, and position updates.

- `backend/state_machine_impl/machine.py`
  - Implements the pick-and-place sequence in a state machine built with `vention-state-machine`.
  - Defines sequential states for: home, move-to-cube, lower-to-pick, close-gripper, lift-cube, move-to-destination, lower-to-place, open-gripper, lift-from-place, complete.
  - Uses asynchronous transition callbacks and background tasks to allow the state machine to progress without blocking the event loop.

- `backend/models/runtime.py`
  - Defines shared runtime state for robot pose, cube and destination coordinates, gripper status, state machine state, motion status, and errors.

### Frontend Architecture

- `frontend/src/App.tsx`
  - Subscribes to backend status updates using a live status stream.
  - Renders telemetry, current state, command buttons, and position configuration forms.
  - Displays connection status and error notifications.

- `frontend/src/api.ts`
  - Implements the client API using `@connectrpc/connect` and generated proto bindings.
  - Sends commands to the backend and receives typed responses.
  - Exposes a `statusStream()` generator for live updates.

- `frontend/src/types.ts`
  - Defines the local TypeScript model for backend status payloads.

- `frontend/src/components/`
  - Contains reusable UI components for telemetry, command controls, state display, and error banners.

### Integration Between Backend and Frontend

- Communication uses a generated RPC contract defined by `proto/app.proto` in both `backend/proto/` and `frontend/proto/`.
- The frontend connects through the `/rpc` endpoint configured by the Vite dev server and Docker Compose fronting.
- The backend uses `vention-communication` to expose RPC actions and a stream. The frontend uses Connect RPC to invoke actions and subscribe to live telemetry.
- The status stream ensures the frontend receives near-real-time updates of robot position, gripper state, and state machine progress.
- User actions (home, start sequence, and position updates) are sent as RPC actions, with the backend returning the current runtime state after each command.

---

## Design Decisions, Assumptions, and Trade-offs

### Design Decisions

- **State machine-based flow**
  - The pick-and-place sequence is modeled explicitly with a state machine. This makes the motion flow deterministic and easier to reason about.

- **Backend runtime state synchronization**
  - The `RobotController` keeps runtime state in sync after every simulator update, ensuring the frontend always sees consistent telemetry.

- **Live status streaming**
  - The frontend relies on a stream rather than frequent polling, reducing backend load and providing smoother UI updates.

- **Docker Compose-first setup**
  - The documented setup relies on containerization so reviewers can run the full stack with a single command.

- **Protocol contract via protobuf**
  - Shared `app.proto` definitions keep frontend and backend contracts aligned and reduce serialization mismatches.

### Assumptions

- The sequence must start from the robot's home state.
- Safe travel is handled by moving the robot to a fixed safe Z height (`200.0`) whenever repositioning horizontally.
- The gripper state changes are instantaneous and do not require motion polling.
- The backend state machine is the single source of truth for sequence progress.
- The frontend should render the latest state even if the user does not explicitly request it.

### Trade-offs

- **Asynchronous state transitions vs simpler blocking flow**
  - Using background asyncio tasks allows the backend to remain responsive, but it also requires careful state updates to avoid race conditions.

- **Simplified gripper control**
  - The gripper open/close actions are treated as instant state changes. This keeps the flow simple, but it is less realistic than modeling gripper motion over time.

- **No persistence layer in current implementation**
  - The app is designed for live simulation, so persistence of configuration is not included in the current containerized flow.

- **Home-first startup requirement**
  - The sequence enforces starting from home to avoid invalid move sequences, but this also means the user must explicitly home the robot before starting.

---

## Notes

- The backend is implemented as a FastAPI app wrapped by `VentionApp`, which automatically generates the necessary RPC wired endpoints.
- The frontend is built with Vite and shipped as a static site inside the Docker Compose stack.
- The Docker Compose topology ensures both services are available together and the frontend can connect to the backend via the same host.

## Misc
- Found an issue in the Vention's [`vention-state-machine`](https://pypi.org/project/vention-state-machine/) library documentation : 

  - `Triggers.<trigger_name>.value` has been replace with `Triggers.<trigger_name>.name` or `Triggers.<trigger_name>()` and must be used accordingly.