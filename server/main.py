from flask import Flask, request, jsonify
from flask_cors import CORS 

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}) 

@app.route("/")
def hello_world():
  return "<p>Hello, World!</p>"

@app.route("/v1/login", methods=['POST'])
def login():
  data = request.get_json()
  email = data.get('email')
  password = data.get('password')
  return jsonify({
    'token': 'fake-token',    
    })

if __name__ == "__main__":
  app.run(debug=True)