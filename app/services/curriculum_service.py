# app/services/curriculum_service.py
from app.services.database import DatabaseService
from fastapi import HTTPException
from datetime import datetime, timezone

class CurriculumService:
    def __init__(self, db_service: DatabaseService):
        self.db = db_service

    async def get_next_study_topic(self) -> dict:
        """
        Lógica del Tutor: Decide qué debe estudiar el alumno hoy.
        Prioridad 1: Temas atrasados (Repaso SRS).
        Prioridad 2: El siguiente tema nuevo en el currículo.
        Prioridad 3: (Fallback) Práctica infinita de los temas más débiles.
        """
        try:
            client = await self.db._get_client()
            now = datetime.now(timezone.utc).isoformat()

            # 1. Buscar temas que necesitan repaso ESTRICTO (SRS)
            reviews = await client.table("user_progress") \
                .select("*, study_topics(*)") \
                .lte("next_review_date", now) \
                .order("next_review_date") \
                .limit(1) \
                .execute()

            if reviews.data:
                topic = reviews.data[0]['study_topics']
                return {"mode": "review", "topic": topic, "progress": reviews.data[0]}

            # 2. Si no hay repasos urgentes, buscar el siguiente tema NUEVO
            latest_progress = await client.table("user_progress") \
                .select("study_topics(order_index)") \
                .order("study_topics(order_index)", desc=True) \
                .limit(1) \
                .execute()
            
            next_index = 1
            if latest_progress.data and latest_progress.data[0]['study_topics']:
                next_index = latest_progress.data[0]['study_topics']['order_index'] + 1

            next_topic = await client.table("study_topics") \
                .select("*") \
                .eq("order_index", next_index) \
                .execute()

            if next_topic.data:
                return {"mode": "learn", "topic": next_topic.data[0], "progress": None}
            
            # 3. EL BUCLE INFINITO (Si llegamos aquí, no hay temas nuevos ni repasos urgentes)
            weakest_topic = await client.table("user_progress") \
                .select("*, study_topics(*)") \
                .order("mastery_level") \
                .order("next_review_date") \
                .limit(1) \
                .execute()

            if weakest_topic.data:
                topic = weakest_topic.data[0]['study_topics']
                return {
                    "mode": "review", 
                    "topic": topic, 
                    "progress": weakest_topic.data[0],
                    "message": "Práctica de Refuerzo" # Podemos usar esto en el frontend si queremos
                }
            else:
                # Literalmente la base de datos de temas está vacía (edge case)
                return {"mode": "mastered", "message": "Tu biblioteca está vacía. Añade temas en Supabase."}

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error en motor de currículo: {str(e)}")