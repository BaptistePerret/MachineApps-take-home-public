"""
State machine module for Gantry Pick & Place backend.

Defines the state machine for orchestrating robot motions and gripper actions.
"""

from .machine import GantryStateMachine, my_state_machine, Triggers

__all__ = [
    "GantryStateMachine",
    "my_state_machine",
    "Triggers",
]
