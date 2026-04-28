# Gantry Pick & Place Frontend

A React + TypeScript dashboard for controlling and monitoring the Gantry Pick & Place robot sequence using Connect-RPC.

## Features

- **Real-time Status Display**: Live telemetry of robot position, gripper state, and current state machine state via streaming
- **Position Configuration**: Set cube start and destination positions via UI
- **Robot Controls**: Home robot and start pick-and-place sequence
- **State Visualization**: See the current step in the pick-and-place sequence
- **Error Handling**: Display errors from the backend clearly
- **Live Streaming**: Real-time updates via Connect-RPC streaming

## Setup

### Install Dependencies

```bash
npm install
```

### Generate API Client

The frontend uses Connect-RPC generated from the backend's Protocol Buffer definitions.

```bash
# Copy proto file from backend
cp ../backend/proto/app.proto ./proto/

# Generate TypeScript client
npm run gen
```

### Development

Start the dev server:

```bash
npm run dev
```

The frontend will connect to the backend at `http://localhost:8000` using Connect-RPC.

### Build

```bash
npm run build
```

Outputs to `dist/`.

## API Integration

The frontend communicates with the backend via **Connect-RPC** (gRPC-Web protocol):

- `getStatus()` — Get current status (unary)
- `homeRobot()` — Trigger home operation (unary)
- `startSequence()` — Start pick-and-place sequence (unary)
- `setCubePosition()` — Set cube start position (unary)
- `setDestinationPosition()` — Set destination position (unary)
- `getCubePosition()` — Get cube start position (unary)
- `getDestinationPosition()` — Get destination position (unary)
- `status()` — **Live streaming** of status updates (server streaming)

## Technologies

- **React 18** — UI framework
- **TypeScript** — Type safety
- **Connect-RPC** — RPC framework for type-safe API calls
- **Protocol Buffers** — API schema definition
- **Buf** — Code generation from proto files
- **CSS3** — Styling

## Project Structure

```
src/
├── components/
│   ├── RobotTelemetryCard.tsx       # Displays robot position, gripper state, etc.
│   ├── PositionConfigurationForm.tsx # Forms to set cube and destination positions
│   ├── CommandButtons.tsx            # Home and Start Sequence buttons
│   ├── StateDisplay.tsx              # Shows current state machine state and progress
│   ├── ErrorBanner.tsx               # Displays errors from backend
│   └── index.ts                      # Component exports
├── api.ts                            # API client (axios)
├── types.ts                          # TypeScript types for API responses
├── App.tsx                           # Main app component with polling logic
├── App.css                           # Main app styles
└── main.tsx                          # React entry point
```

## API Integration

The frontend communicates with the backend via REST endpoints:

- `POST /api/get_status` — Get current status
- `POST /api/home_robot` — Trigger home operation
- `POST /api/start_sequence` — Start pick-and-place sequence
- `POST /api/set_cube_position` — Set cube start position
- `POST /api/set_destination_position` — Set destination position
- `POST /api/get_cube_position` — Get cube start position
- `POST /api/get_destination_position` — Get destination position

## Technologies

- **React 18** — UI framework
- **TypeScript** — Type safety
- **Vite** — Build tool
- **Axios** — HTTP client
- **CSS3** — Styling
