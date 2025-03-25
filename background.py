from flask import Flask
from threading import Thread
import logging

# Disable Flask's default logger
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask('')

@app.route('/')
def home():
    return "I'm alive"

def run():
    app.run(host='0.0.0.0', port=3000, threaded=True)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True  # Set as daemon thread
    t.start()
    return t
