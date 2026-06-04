from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from db import db
from datetime import datetime
import gunicorn
app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- MONGODB COLLECTIONS ----------------
users = db["users"]
notes = db["notes"]

dsa = db["dsa"]
ml = db["ml"]
fullstack = db["fullstack"]
aptitude = db["aptitude"]


# ---------------- HOME ----------------
@app.route('/')
def home():
    if "user" in session:
        return redirect('/dashboard')
    return redirect('/login')


# ---------------- REGISTER ----------------
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        if users.find_one({"email": email}):
            return "Email already exists"

        users.insert_one({
            "name": name,
            "email": email,
            "password": generate_password_hash(password)
        })

        return redirect('/login')

    return render_template('register.html')


# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        user = users.find_one({"email": email})

        if user and check_password_hash(user['password'], password):

            session['user'] = user['name']
            session['email'] = user['email']

            return redirect('/dashboard')

        return "Invalid Credentials"

    return render_template('login.html')


# ---------------- DASHBOARD ----------------
@app.route('/dashboard')
def dashboard():

    if 'user' not in session:
        return redirect('/login')

    user_notes = list(
        notes.find({"user": session['email']})
        .sort("created_at", -1)
        .limit(3)
    )

    return render_template(
        'dashboard.html',
        username=session['user'],
        notes=user_notes
    )


# ---------------- NOTES ----------------
@app.route('/notes', methods=['GET', 'POST'])
def notes_page():

    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':

        notes.insert_one({
            "user": session['email'],
            "title": request.form['title'],
            "content": request.form['content'],
            "subject": request.form['subject'],
            "created_at": datetime.now()
        })

        return redirect('/notes')

    data = list(notes.find({"user": session['email']}))
    return render_template('notes.html', notes=data)


# ---------------- GENERIC MODULE FUNCTION ----------------
def handle_module(collection, template):

    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':

        collection.insert_one({
            "user": session['email'],
            "topic": request.form['topic'],
            "status": request.form['status'],
            "created_at": datetime.now()
        })

        return redirect(request.path)

    data = list(collection.find({"user": session['email']}))
    return render_template(template, data=data)


# ---------------- DSA ----------------
@app.route('/dsa', methods=['GET', 'POST'])
def dsa_page():
    return handle_module(dsa, 'dsa.html')


# ---------------- ML ----------------
@app.route('/ml', methods=['GET', 'POST'])
def ml_page():
    return handle_module(ml, 'ml.html')


# ---------------- FULL STACK ----------------
@app.route('/fullstack', methods=['GET', 'POST'])
def fullstack_page():
    return handle_module(fullstack, 'fullstack.html')


# ---------------- APTITUDE ----------------
@app.route('/aptitude', methods=['GET', 'POST'])
def aptitude_page():
    return handle_module(aptitude, 'aptitude.html')


# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(debug=True)