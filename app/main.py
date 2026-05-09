# app/main.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Schemas
from app.schemas.analysis import JapaneseAnalysisResponse
from app.schemas.quiz import QuizQuestion, TopicQuiz
from app.schemas.lesson import LessonContent

# Services
from app.services.database import DatabaseService
from app.services.ai_service import AIService
from app.services.curriculum_service import CurriculumService
from app.services.lesson_service import LessonService
from app.services.quiz_service import QuizService
from app.services.progress_service import ProgressService
from app.agents.graph import orchestrator

app = FastAPI(title="Sensei-Flow AI: Tutor System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Dependency Injection ---
def get_db(): return DatabaseService()
def get_curriculum(db: DatabaseService = Depends(get_db)): return CurriculumService(db)
def get_lesson(): return LessonService()
def get_progress(db: DatabaseService = Depends(get_db)): return ProgressService(db)
def get_quiz_service(db: DatabaseService = Depends(get_db)): return QuizService(db)

# --- Endpoints ---

@app.post("/analyze", response_model=JapaneseAnalysisResponse)
async def analyze(text: str):
    # Lógica de análisis morfológico original
    state = {"input_text": text, "errors": []}
    result = await orchestrator.app.ainvoke(state)
    return result["analysis"]

@app.get("/tutor/next", description="Decide qué estudiar hoy")
async def get_next_step(curr: CurriculumService = Depends(get_curriculum)):
    return await curr.get_next_study_topic()

@app.get("/tutor/lesson/{topic_id}", response_model=LessonContent)
async def get_lesson_content(topic_id: str, 
                           db: DatabaseService = Depends(get_db),
                           ls: LessonService = Depends(get_lesson)):
    # 1. Obtener el tema de la DB
    client = await db._get_client()
    topic = await client.table("study_topics").select("*").eq("id", topic_id).single().execute()
    if not topic.data: raise HTTPException(status_code=404, detail="Tema no encontrado")
    
    # 2. Generar lección con IA
    return await ls.generate_lesson(topic.data)

@app.post("/tutor/quiz/submit")
async def submit_quiz_result(topic_id: str, 
                           success: bool, 
                           ps: ProgressService = Depends(get_progress)):
    # Actualiza el SRS del alumno
    await ps.update_mastery(topic_id, success)
    return {"status": "progress_updated"}

@app.get("/history")
async def get_history(db: DatabaseService = Depends(get_db)):
    return await db.get_recent_analyses()

@app.get("/tutor/progress")
async def get_user_progress(ps: ProgressService = Depends(get_progress)):
    """Devuelve la lista de temas vistos y su nivel de maestría."""
    return await ps.get_all_progress()

@app.get("/tutor/quiz/{topic_id}", response_model=TopicQuiz)
async def get_topic_quiz(topic_id: str, 
                         db: DatabaseService = Depends(get_db),
                         qs: QuizService = Depends(get_quiz_service)):
    """Genera un examen dinámico para el tema actual."""
    client = await db._get_client()
    topic = await client.table("study_topics").select("*").eq("id", topic_id).single().execute()
    if not topic.data:
        raise HTTPException(status_code=404, detail="Tema no encontrado")
    
    return await qs.generate_topic_quiz(topic.data)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)