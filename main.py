import os
from flask import Flask, request, send_from_directory
from pynput.keyboard import Controller, Key
import threading
import time

app = Flask(__name__)
keyboard = Controller()
should_stop = threading.Event()
lock = threading.Lock()
typing_speed = 0.1  # Default typing speed

# Hardcoded path to the 'public' folder relative to the main.py file
PUBLIC_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'public')

def type_text(text):
    global typing_speed
    lines = text.split('\n')
    for line in lines:
        for char in line:
            with lock:
                if should_stop.is_set():
                    return

            keyboard.type(char)
            time.sleep(typing_speed)
            if(char == '{'):
                keyboard.press(Key.right)
                keyboard.release(Key.right)
                time.sleep(typing_speed)
                keyboard.press(Key.backspace)
                keyboard.release(Key.backspace)
                time.sleep(typing_speed)
        time.sleep(typing_speed)
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)
        time.sleep(typing_speed)
        keyboard.press(Key.home)
        keyboard.release(Key.home)
        time.sleep(typing_speed)

@app.route('/type', methods=['POST'])
def handle_type():
    with lock:
        should_stop.clear()

    if request.method == 'POST':
        data = request.get_json()
        text = data['text']
        threading.Thread(target=type_text, args=(text,)).start()
        return '', 200
    else:
        return '', 405

@app.route('/stop', methods=['POST'])
def handle_stop():
    if request.method == 'POST':
        with lock:
            should_stop.set()
        return '', 200
    else:
        return '', 405

@app.route('/speed', methods=['POST'])
def handle_speed():
    global typing_speed
    if request.method == 'POST':
        data = request.get_json()
        speed = data['speed']
        with lock:
            typing_speed = speed
        return '', 200
    else:
        return '', 405

@app.route('/')
def serve_index():
    return send_from_directory(PUBLIC_FOLDER, 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
