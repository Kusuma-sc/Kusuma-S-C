from flask import Flask, render_template, request, session, redirect
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.secret_key = "secret123"

socketio = SocketIO(app, cors_allowed_origins="*")

users = {}

# ---------------- ROUTES ---------------- #

@app.route('/')
def login():
    return render_template("login.html")

@app.route('/dashboard', methods=['POST'])
def dashboard():
    email = request.form.get("email")
    session['email'] = email
    return render_template("dashboard.html", email=email)

@app.route('/call')
def call():
    if 'email' not in session:
        return redirect("/")
    target = request.args.get("target")
    return render_template("call.html", email=session['email'], target=target)

# ---------------- SOCKET ---------------- #

@socketio.on('connect')
def connect():
    if 'email' in session:
        users[session['email']] = request.sid
        print("Connected:", session['email'])

@socketio.on('disconnect')
def disconnect():
    if 'email' in session:
        users.pop(session['email'], None)

# 📞 CALL REQUEST
@socketio.on('call_user')
def call_user(data):
    target = data['to']
    caller = data['from']

    print("Calling:", target)

    if target in users:
        emit('incoming_call', {'from': caller}, to=users[target])

# ✅ ACCEPT CALL
@socketio.on('accept_call')
def accept_call(data):
    caller = data['to']
    receiver = data['from']

    if caller in users:
        emit('call_accepted', {'from': receiver}, to=users[caller])

# ❌ REJECT CALL
@socketio.on('reject_call')
def reject_call(data):
    caller = data['to']

    if caller in users:
        emit('call_rejected', {}, to=users[caller])

# 💬 CHAT
@socketio.on('send_message')
def message(data):
    emit('receive_message', data, broadcast=True)

# ---------------- RUN ---------------- #

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=10000)