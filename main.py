from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Ye har jagah se access allow karega
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from supabase import create_client, Client
import json, os, sys
from datetime import datetime
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# AI Engine
from vision_engine import get_face_encoding_from_base64, match_face

app = FastAPI(title="GCT Multan Attendance")

# --- PATH LOGIC (EXE Compatible) ---
def get_resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        # Jab EXE chal rahi ho
        return os.path.join(sys._MEIPASS, relative_path)
    return relative_path

STATIC_DIR = get_resource_path("static")

# Supabase Keys (Wahi jo tumne pehle di thin)
SUPABASE_URL = "https://gazjbujwpbshxpbsagbn.supabase.co"
SUPABASE_KEY = "sb_publishable_JFaFDHaVymZYEm58jXNzxw_AgUzFMQY"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Static files mount
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Models
class StudentRegistration(BaseModel):
    name: str
    roll_no: str
    image_base64: str

class AttendanceRequest(BaseModel):
    image_base64: str

# --- 1. HOME SCREEN (FIXED PATH) ---
@app.get("/")
def serve_ui():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"error": f"Path not found: {index_file}"}

# --- 2. API ENDPOINTS (As it is) ---
@app.post("/api/register")
def register_student(student: StudentRegistration):
    encoding, message = get_face_encoding_from_base64(student.image_base64)
    if encoding is None:
        raise HTTPException(status_code=400, detail=message)
    try:
        data = {"roll_no": student.roll_no, "name": student.name, "face_encoding": json.dumps(encoding)}
        supabase.table("students").insert(data).execute()
        return {"status": "success", "message": f"Student {student.name} saved!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/recognize")
def mark_attendance(req: AttendanceRequest):
    unknown_encoding, message = get_face_encoding_from_base64(req.image_base64)
    if unknown_encoding is None: raise HTTPException(status_code=400, detail=message)
    
    response = supabase.table("students").select("*").execute()
    students = response.data
    if not students: raise HTTPException(status_code=404, detail="Vault empty")
    
    known_encodings = [json.loads(s['face_encoding']) for s in students]
    match_idx = match_face(unknown_encoding, known_encodings)
    
    if match_idx != -1:
        matched_student = students[match_idx]
        now = datetime.now()
        attendance_data = {
            "roll_no": matched_student['roll_no'],
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%I:%M:%S %p"),
            "status": "Present"
        }
        supabase.table("attendance").insert(attendance_data).execute()
        return {"status": "success", "message": f"Welcome {matched_student['name']}!", "student": matched_student}
    else:
        raise HTTPException(status_code=401, detail="Face NOT Recognized")