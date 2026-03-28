users = {}

# 🔥 REGISTER USER (IMPORTANT)
@socketio.on('register')
def register(data):
    email = data['email']
    users[email] = request.sid
    print("REGISTER:", email)

# REMOVE OLD connect() SESSION LOGIC ❌

@socketio.on('disconnect')
def disconnect():
    for email, sid in list(users.items()):
        if sid == request.sid:
            users.pop(email)
            print("DISCONNECT:", email)

# 📞 CALL USER
@socketio.on('call_user')
def call_user(data):
    caller = data['from']
    target = data['to']

    print("CALL:", caller, "→", target)

    if target in users:
        emit('incoming_call', {'from': caller}, to=users[target])
    else:
        print("TARGET NOT ONLINE")

# ✅ ACCEPT
@socketio.on('accept_call')
def accept_call(data):
    caller = data['to']
    receiver = data['from']

    if caller in users:
        emit('call_accepted', {'from': receiver}, to=users[caller])

# ❌ REJECT
@socketio.on('reject_call')
def reject_call(data):
    caller = data['to']

    if caller in users:
        emit('call_rejected', {}, to=users[caller])