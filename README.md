# Carmensita Chatbot GUI

A Flask-based local web GUI for a chatbot featuring a layered CSS sprite system, manga-style typewriter speech bubbles, and a tropical green/soft pink dynamic chat interface.

## Prerequisites
- Python 3.x
- Flask

## Setup

1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

2. Add your sprite PNGs into `static/sprites/`:
   - `body_base.png` (Idle breathing body)
   - `body_talking.png` (Body shown while typing)
   - `face_happy.png`
   - `face_sad.png`
   - `face_neutral.png`
   - `face_flirty.png`
   - `face_surprised.png`
   - `eyes_blink.png` (Blinks overlay)
   
   *Tip: Empty placeholders will display automatically if any PNGs are missing, preventing the app from crashing while keeping the UI intact.*

3. Add your background image:
   Place it at `static/bg/background.jpg` or `static/bg/background.png`. If neither are found, a dark green gradient fallback is automatically rendered.

## Run Application

1. Start the Flask server:
   ```bash
   python app.py
   ```
2. The web browser will auto-launch and load the application at http://127.0.0.1:5000.
