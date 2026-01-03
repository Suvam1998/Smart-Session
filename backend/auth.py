from jose import jwt
import time
import uuid

SECRET_KEY = "SMARTSESSION_SECRET"
ALGORITHM = "HS256"

def create_session_token():
    session_id = str(uuid.uuid4())
    payload = {
        "session_id": session_id,
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600  # 1 hour
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token, session_id

def decode_token(token):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
