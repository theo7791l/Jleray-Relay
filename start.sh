#!/bin/bash
pip install -r requirements.txt -q
uvicorn app.main:app --host 0.0.0.0 --port 7435 --reload
