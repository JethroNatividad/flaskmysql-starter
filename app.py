from flask import Flask, jsonify, request
from bcrypt import hashpw, checkpw, gensalt
import jwt
import mysql.connector

### config ###
app = Flask(__name__)
db = mysql.connector.connect(
  host="127.0.0.1",
  user="root",
  password="1234",
  database='db'
)
cursor = db.cursor(dictionary=True)

def gentoken(payload):
    return jwt.encode(payload, 'superverysecretkey', algorithm='HS256')

### Routes ###
# Register
@app.route('/register', methods=['POST'])
def register():
    body = request.json
    name = body.get('name')
    email = body.get('email')
    password = body.get('password')
    if not email or not name or not password:
        return jsonify({'error': 'name, email and password are required'})
    
   
    #check if user exist in database
    cursor.execute(f'SELECT * FROM user WHERE email = "{email}"')
    user = cursor.fetchone()
    if user != None:
        return jsonify({'message': 'User Already Exists'})
    # hash the password and save to db
    hashedPassword = hashpw(password.encode(), gensalt(12))
    cursor.execute(f'INSERT INTO user (name, email, password) VALUES ("{name}", "{email}", "{hashedPassword.decode()}")')
    db.commit()
    return jsonify({
        'message': 'Successfully registered',
    })


# Login
@app.route('/login', methods=['POST'])
def login():
    body = request.json
    email = body.get('email')
    password = body.get('password')
    #all fields are required
    if not email or not password:
        return jsonify({'error': 'email and password are required'})

    #check if user exist in database
    cursor.execute(f'SELECT * FROM user WHERE email = "{email}"')
    user = cursor.fetchone()
    if user == None:
        return jsonify({'message': 'User does not exist, please register'})
    #check if password match
    isValid = checkpw(password.encode(), user.get('password').encode())
    if isValid:
        token = gentoken({'id': str(user['id']), 'name': user['name']})
        return jsonify({
            'message': 'Successfully logged in',
            'token': token.decode()
        })
    else:
        return jsonify({'message': 'Incorrect password'})


# show all users
@app.route('/users')
def show_users():
    cursor.execute('SELECT name, email FROM user')
    users = cursor.fetchall()
    return jsonify({'users': users})


# show single user
@app.route('/users/<userId>')
def show_user(userId):
    cursor.execute(f'SELECT name, email FROM user WHERE id = {userId}')
    user = cursor.fetchone()
    if (user == None):
        return jsonify({'msg': 'User not found'})
    return jsonify({'user': user})


if __name__ == '__main__':
    app.run(debug=True)