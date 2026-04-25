#!/bin/bash
# Start the Gantry Pick & Place backend with uvicorn

uvicorn app:fastapi_app --reload --host 0.0.0.0 --port 8000