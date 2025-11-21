 # Visual Inventory & QA Agent — Starter Repo
 **Track:** Enterprise Agents
 This repository is a starter scaffold for the Kaggle Capstone project: a multi
agent system that automates inventory counting and visual QA from images. It 
includes a small Flask demo, models, and a sample dataset generator.
 ## What is included- `app.py` — Flask demo with endpoints for uploading images and listing results.- `models.py` — SQLAlchemy models and DB init.- `sample_data.py` — Generates placeholder images and a sample inventory CSV to 
test the demo.
 ## Quickstart (local)
 1. Create a Python venv and install dependencies (example):
 ```bash
 python -m venv venv
 source venv/bin/activate  # Windows: venv\Scripts\activate
 pip install flask sqlalchemy pillow flask_sqlalchemy
 python sample_data.py
 python app.py