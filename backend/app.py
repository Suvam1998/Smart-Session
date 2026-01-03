from fastapi import FastAPI, WebSocket, Query
from fastapi.responses import JSONResponse
import base64, cv2, numpy as np
from vision import VisionEngine
from auth import create_session_token, decode_token

app = FastAPI()
vision = VisionEngine()

# session_id -> list of websockets
sessions = {}

@app.post("/create-session")
def create_session():
    token, session_id = create_session_token()
    sessions[session_id] = []
    return {
        "session_link": f"http://localhost:8000/student.html?token={token}"
    }

@app.websocket("/ws")
async def websocket_endpoint(
    ws: WebSocket,
    token: str = Query(...)
):
    await ws.accept()

    payload = decode_token(token)
    session_id = payload["session_id"]

    if session_id not in sessions:
        sessions[session_id] = []

    sessions[session_id].append(ws)

    try:
        while True:
            data = await ws.receive_text()

            # Teacher dashboards do NOT send video
            if data.startswith("data:image"):
                frame = decode_image(data)
                telemetry = vision.analyze(frame)

                for client in sessions[session_id]:
                    await client.send_json(telemetry)

    except:
        sessions[session_id].remove(ws)

def decode_image(data):
    img_bytes = base64.b64decode(data.split(",")[1])
    np_img = np.frombuffer(img_bytes, np.uint8)
    return cv2.imdecode(np_img, cv2.IMREAD_COLOR)
