"""
Gantry Pick & Place Backend Application

Entry point for the FastAPI backend using vention-communication and vention-state-machine.

Run with: uvicorn app:app --reload
"""

from fastapi import FastAPI
from communication.app import VentionApp

# Create the VentionApp instance
app = VentionApp(name="GantryPickAndPlace", emit_proto=True)

# TODO: Register RPC actions and streams here
# TODO: Integrate state machine

# Finalize the app to register routes and emit proto
app.finalize()

# Expose the FastAPI app for uvicorn
fastapi_app = app

print("Gantry Pick & Place backend is running...")