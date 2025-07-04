from flask import Flask, render_template
import os

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-key-for-testing'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True) 