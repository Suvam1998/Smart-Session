from pydantic import BaseModel

class Telemetry(BaseModel):
    emotion: str
    gaze: str
    face_count: int
    alert: str
    timestamp: float
