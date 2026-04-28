/**
 * Shared types for the Gantry Pick & Place frontend
 */

export interface Position {
  x: number;
  y: number;
  z: number;
}

export interface StatusResponse {
  robot_position: Position;
  home_position: Position;
  cube_start_position: Position;
  destination_position: Position;
  gripper_state: string;
  state_machine_state: string;
  is_moving: boolean;
  error: string | null;
}

export type GripperState = 'OPEN' | 'CLOSED';
