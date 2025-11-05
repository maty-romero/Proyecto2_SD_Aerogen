from flask import Flask, request, jsonify
import jwt

app = Flask(__name__)
secret_key = "secret"

@app.route('/')
def hello():
    return '<h1>Hello, World!</h1>'


@app.route('/login', methods=['POST'])
def login():
    try:
        username = request.json.get('username')
        password = request.json.get('password')
        if username is None or password is None:
            return jsonify({'message': 'Both username and password are required'}), 400
        if username == "admin" and password == "123":
            token = jwt.encode({'password': password}, secret_key, algorithm='HS256')
            return jsonify({'token': token}), 200
        
        return jsonify({'message': 'Authentication failed'}), 401
    except Exception as e:
        print(e)
        return jsonify({'message': 'Internal server error'}), 500

def verify_token(func):
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization', '')
        if not token:
            return jsonify({'message': 'Token not provided'}), 401
        token_parts = token.split(" ")
        if len(token_parts) != 2 or token_parts[0].lower() != 'bearer':
            return jsonify({'message': 'Invalid token format'}), 401
        token = token_parts[1]
        try:
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            request.password = payload['password']
            return func(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expired'}), 403
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 403
    return wrapper

@app.route('/protected', methods=['GET'])
@verify_token
def protected():
    return jsonify({'message': 'You have access'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
