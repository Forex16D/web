from flask import Flask, request, jsonify
from flask_cors import CORS 
from auth.login import login
from middleware import token_required

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}) 

@app.route("/")
def hello_world():
  return "<p>Hello, World!</p>"

@app.route("/v1/login", methods=['POST'])
def handle_login():
  return login(request)

@app.route("/v1/protected", methods=['GET'])
@token_required
def protected_route(current_user):
  return jsonify({"message": f"Hello {current_user}, this is a protected route!"})

if __name__ == "__main__":
  app.run(debug=True)