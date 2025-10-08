from flask import Flask, jsonify
from flask_cors import CORS
    
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
    
@app.route('/python/hello')
def hello_world():
    return jsonify({
        "message": "Hello from Python!",
        "source": "python-api"
    })
    
if __name__ == '__main__':
    app.run(port=5000)