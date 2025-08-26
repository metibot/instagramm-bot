import threading
from flask import Flask
from bot.scheduler import run_scheduler

# Flask app for health check
app = Flask(__name__)

@app.route("/health")
def health():
    return "OK", 200

def run_health_server():
    app.run(host="0.0.0.0", port=8080)

if name == "__main__":
    # Run health server in background thread
    threading.Thread(target=run_health_server, daemon=True).start()

    # Start main bot scheduler loop
    run_scheduler()
