from flask import Flask, render_template, request, session, redirect
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.secret_key = "secret123"

socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

users = {}

# ---------------- ROUTES ---------------- #

@app.route('/')
def login():
    return render_template("login.html")


@app.route('/dashboard', methods=['POST'])
def dashboard():
    email = request.form.get("email")

    if not email:
        return redirect("/")

    session['email'] = email
    return render_template("dashboard.html", email=email)


@app.route('/call')
def call():
    if 'email' not in session:
        return redirect("/")
    return render_template("call.html", email=session['email'])


# ---------------- SOCKET ---------------- #
@app.route('/call')
def call():
    if 'email' not in session:
        return redirect("/")

    target = request.args.get("target")  # ✅ IMPORTANT

    return render_template("call.html",
                           email=session['email'],
                           target=target)
@socketio.on('connect')
def connect():
    if 'email' in session:
        users[session['email']] = request.sid


@socketio.on('disconnect')
def disconnect():
    if 'email' in session:
        users.pop(session['email'], None)


# 📩 CHAT
@socketio.on('send_message')
def handle_message(data):
    emit('receive_message', data, broadcast=True)
    https: // kusuma - s - c - 2.
    onrender.com


# 📞 CALL REQUEST
@socketio.on('call_user')
def call_user(data):
    target = data['to']
    if target in users:
        emit('incoming_call', data, to=users[target])


# ❌ REJECT CALL
@socketio.on('reject_call')
def reject_call(data):
    target = data['to']
    if target in users:
        emit('call_rejected', {}, to=users[target])


# 📡 WEBRTC
@socketio.on('webrtc_offer')
def offer(data):
    target = data['to']
    if target in users:
        emit('webrtc_offer', data, to=users[target])


@socketio.on('webrtc_answer')
def answer(data):
    target = data['to']
    if target in users:
        emit('webrtc_answer', data, to=users[target])


@socketio.on('ice_candidate')
def ice(data):
    target = data['to']
    if target in users:
        emit('ice_candidate', data, to=users[target])


# ---------------- RUN ---------------- #

if __name__ == "__main__":
    socketio.run(app, debug=True)