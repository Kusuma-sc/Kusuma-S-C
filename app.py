from flask import Flask, render_template, request, session, redirect
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.secret_key = "secret123"

socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

users = {}

# ---------- ROUTES ---------- #

@app.route('/')
def login():
    return render_template("login.html")

@app.route('/dashboard', methods=['POST'])
def dashboard():
    email = request.form.get("email")
    password = request.form.get("password")

    if not email or not password:
        return redirect("/")

    session['email'] = email
    return render_template("dashboard.html", email=email)

@app.route('/call')
def call():
    if 'email' not in session:
        return redirect("/")
    target = request.args.get("target")
    return render_template("call.html", email=session['email'], target=target)

# ---------- SOCKET ---------- #

@socketio.on('register')
def register(data):
    users[data['email']] = request.sid

@socketio.on('disconnect')
def disconnect():
    for email, sid in list(users.items()):
        if sid == request.sid:
            users.pop(email)
            break

@socketio.on('call_user')
def call_user(data):
    if data['to'] in users:
        emit('incoming_call', {'from': data['from']}, to=users[data['to']])

@socketio.on('accept_call')
def accept_call(data):
    if data['to'] in users:
        emit('call_accepted', {'from': data['from']}, to=users[data['to']])

@socketio.on('reject_call')
def reject_call(data):
    if data['to'] in users:
        emit('call_rejected', {}, to=users[data['to']])

@socketio.on('send_message')
def message(data):
    emit('receive_message', data, broadcast=True)

# ---------- RUN ---------- #

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=10000)