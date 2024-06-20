from flask import Flask, jsonify
import json
import os
import subprocess
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})

@app.route('/api/test', methods=['GET'])
def test_endpoint():
    return jsonify({"message": "Test endpoint working!"})

@app.route('/api/odds', methods=['GET'])
def get_odds():
    json_path = os.path.join(os.path.dirname(__file__), 'odds.json')
    if os.path.exists(json_path):
        with open(json_path, 'r') as f:
            data = json.load(f)
        return jsonify(data)
    else:
        return jsonify({"error": "File not found"}), 404

def run_main_script():
    try:
        result = subprocess.run(['python3', 'main.py'], capture_output=True, text=True)
        if result.returncode == 0:
            print("Main script executed successfully.")
        else:
            print(f"Main script error: {result.stderr}")
    except Exception as e:
        print(f"Error running main script: {e}")

if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=run_main_script, trigger="interval", minutes=2)
    scheduler.start()
    
    run_main_script()
    
    atexit.register(lambda: scheduler.shutdown())

    app.run(debug=True, port=5001)
