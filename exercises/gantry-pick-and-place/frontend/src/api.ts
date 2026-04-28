/**
 * API client for Gantry Pick & Place backend using Connect-RPC
 */

import { createClient } from "@connectrpc/connect";
import { createConnectTransport } from "@connectrpc/connect-web";
import { GantryPickAndPlaceService } from "./gen/app_connect.js";

// Create transport
const transport = createConnectTransport({
  baseUrl: "/rpc", // Use Vite proxy to forward to backend
  useBinaryFormat: false,
});

// Create client
const client = createClient(GantryPickAndPlaceService, transport);

export const api = {
  /**
   * Get current robot and state machine status
   */
  async getStatus() {
    const response = await client.get_status({});
    return {
      robot_position: {
        x: response.robotPosition?.x || 0,
        y: response.robotPosition?.y || 0,
        z: response.robotPosition?.z || 0,
      },
      home_position: {
        x: response.homePosition?.x || 0,
        y: response.homePosition?.y || 0,
        z: response.homePosition?.z || 0,
      },
      cube_start_position: {
        x: response.cubeStartPosition?.x || 0,
        y: response.cubeStartPosition?.y || 0,
        z: response.cubeStartPosition?.z || 0,
      },
      destination_position: {
        x: response.destinationPosition?.x || 0,
        y: response.destinationPosition?.y || 0,
        z: response.destinationPosition?.z || 0,
      },
      gripper_state: response.gripperState || "OPEN",
      state_machine_state: response.stateMachineState || "ready",
      is_moving: response.isMoving || false,
      error: response.error || null,
    };
  },

  /**
   * Trigger home operation
   */
  async homeRobot() {
    const response = await client.home_robot({});
    return {
      robot_position: {
        x: response.robotPosition?.x || 0,
        y: response.robotPosition?.y || 0,
        z: response.robotPosition?.z || 0,
      },
      home_position: {
        x: response.homePosition?.x || 0,
        y: response.homePosition?.y || 0,
        z: response.homePosition?.z || 0,
      },
      cube_start_position: {
        x: response.cubeStartPosition?.x || 0,
        y: response.cubeStartPosition?.y || 0,
        z: response.cubeStartPosition?.z || 0,
      },
      destination_position: {
        x: response.destinationPosition?.x || 0,
        y: response.destinationPosition?.y || 0,
        z: response.destinationPosition?.z || 0,
      },
      gripper_state: response.gripperState || "OPEN",
      state_machine_state: response.stateMachineState || "ready",
      is_moving: response.isMoving || false,
      error: response.error || null,
    };
  },

  /**
   * Start the pick-and-place sequence
   */
  async startSequence() {
    const response = await client.start_sequence({});
    return {
      robot_position: {
        x: response.robotPosition?.x || 0,
        y: response.robotPosition?.y || 0,
        z: response.robotPosition?.z || 0,
      },
      home_position: {
        x: response.homePosition?.x || 0,
        y: response.homePosition?.y || 0,
        z: response.homePosition?.z || 0,
      },
      cube_start_position: {
        x: response.cubeStartPosition?.x || 0,
        y: response.cubeStartPosition?.y || 0,
        z: response.cubeStartPosition?.z || 0,
      },
      destination_position: {
        x: response.destinationPosition?.x || 0,
        y: response.destinationPosition?.y || 0,
        z: response.destinationPosition?.z || 0,
      },
      gripper_state: response.gripperState || "OPEN",
      state_machine_state: response.stateMachineState || "ready",
      is_moving: response.isMoving || false,
      error: response.error || null,
    };
  },

  /**
   * Set cube start position
   */
  async setCubePosition(position: { x: number; y: number; z: number }) {
    const response = await client.set_cube_position({
      x: position.x,
      y: position.y,
      z: position.z,
    });
    return {
      robot_position: {
        x: response.robotPosition?.x || 0,
        y: response.robotPosition?.y || 0,
        z: response.robotPosition?.z || 0,
      },
      home_position: {
        x: response.homePosition?.x || 0,
        y: response.homePosition?.y || 0,
        z: response.homePosition?.z || 0,
      },
      cube_start_position: {
        x: response.cubeStartPosition?.x || 0,
        y: response.cubeStartPosition?.y || 0,
        z: response.cubeStartPosition?.z || 0,
      },
      destination_position: {
        x: response.destinationPosition?.x || 0,
        y: response.destinationPosition?.y || 0,
        z: response.destinationPosition?.z || 0,
      },
      gripper_state: response.gripperState || "OPEN",
      state_machine_state: response.stateMachineState || "ready",
      is_moving: response.isMoving || false,
      error: response.error || null,
    };
  },

  /**
   * Set destination position
   */
  async setDestinationPosition(position: { x: number; y: number; z: number }) {
    const response = await client.set_destination_position({
      x: position.x,
      y: position.y,
      z: position.z,
    });
    return {
      robot_position: {
        x: response.robotPosition?.x || 0,
        y: response.robotPosition?.y || 0,
        z: response.robotPosition?.z || 0,
      },
      home_position: {
        x: response.homePosition?.x || 0,
        y: response.homePosition?.y || 0,
        z: response.homePosition?.z || 0,
      },
      cube_start_position: {
        x: response.cubeStartPosition?.x || 0,
        y: response.cubeStartPosition?.y || 0,
        z: response.cubeStartPosition?.z || 0,
      },
      destination_position: {
        x: response.destinationPosition?.x || 0,
        y: response.destinationPosition?.y || 0,
        z: response.destinationPosition?.z || 0,
      },
      gripper_state: response.gripperState || "OPEN",
      state_machine_state: response.stateMachineState || "ready",
      is_moving: response.isMoving || false,
      error: response.error || null,
    };
  },

  /**
   * Get cube start position
   */
  async getCubePosition() {
    const response = await client.get_cube_position({});
    return {
      x: response.x || 0,
      y: response.y || 0,
      z: response.z || 0,
    };
  },

  /**
   * Get destination position
   */
  async getDestinationPosition() {
    const response = await client.get_destination_position({});
    return {
      x: response.x || 0,
      y: response.y || 0,
      z: response.z || 0,
    };
  },

  /**
   * Subscribe to status stream
   */
  async *statusStream() {
    const stream = client.status({});
    for await (const response of stream) {
      yield {
        robot_position: {
          x: response.robotPosition?.x || 0,
          y: response.robotPosition?.y || 0,
          z: response.robotPosition?.z || 0,
        },
        home_position: {
          x: response.homePosition?.x || 0,
          y: response.homePosition?.y || 0,
          z: response.homePosition?.z || 0,
        },
        cube_start_position: {
          x: response.cubeStartPosition?.x || 0,
          y: response.cubeStartPosition?.y || 0,
          z: response.cubeStartPosition?.z || 0,
        },
        destination_position: {
          x: response.destinationPosition?.x || 0,
          y: response.destinationPosition?.y || 0,
          z: response.destinationPosition?.z || 0,
        },
        gripper_state: response.gripperState || "OPEN",
        state_machine_state: response.stateMachineState || "ready",
        is_moving: response.isMoving || false,
        error: response.error || null,
      };
    }
  },
};
