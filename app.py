from flask import Flask, request, jsonify
import json
from datetime import datetime
import os

app = Flask(__name__)

@app.route('/api/v1/receiver', methods=['POST'])
def receive_message():
    try:
        data = request.get_json()
        print(f"\n{'='*60}")
        print(f"[{datetime.now()}] Message received from Bosun")
        print(f"{'='*60}")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        print(f"{'='*60}\n")
        
        response = {
            "status": "success",
            "message": "Message received successfully",
            "timestamp": datetime.now().isoformat()
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"Error processing message: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "Service is running"}), 200

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "name": "Bosun IoT Platform Webhook Receiver",
        "version": "1.0",
        "endpoints": {
            "receiver": "/api/v1/receiver",
            "health": "/health"
        }
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
