# main.py
from flask import Flask, jsonify
import json
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/odds', methods=['GET'])
def get_odds():
    json_path = os.path.join(os.path.dirname(__file__), 'odds.json')
    with open(json_path, 'r') as f:
        data = json.load(f)
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)