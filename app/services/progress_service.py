# app/services/progress_service.py
from datetime import datetime, timedelta, timezone
from app.services.database import DatabaseService

class ProgressService:
    def __init__(self, db_service: DatabaseService):
        self.db = db_service

    async def update_mastery(self, topic_id: str, success: bool):
        """
        Calcula la próxima revisión basándose en el éxito o fracaso.
        Lógica:
        - Si aciertas: El intervalo aumenta (1 día, 3 días, 7 días, 30 días).
        - Si fallas: El intervalo vuelve a 1 día y baja el nivel de maestría.
        """
        client = await self.db._get_client()
        
        # Obtener progreso actual
        current = await client.table("user_progress").select("*").eq("topic_id", topic_id).execute()
        
        mastery = 0
        if current.data:
            mastery = current.data[0]['mastery_level']
        
        if success:
            mastery = min(mastery + 1, 5)
            # Intervalos en días: 1, 3, 7, 14, 30
            days = [1, 3, 7, 14, 30][mastery - 1] if mastery > 0 else 1
        else:
            mastery = max(mastery - 1, 1)
            days = 1
            
        next_review = datetime.now(timezone.utc) + timedelta(days=days)
        
        await client.table("user_progress").upsert({
            "topic_id": topic_id,
            "mastery_level": mastery,
            "next_review_date": next_review.isoformat(),
            "total_reviews": (current.data[0]['total_reviews'] + 1) if current.data else 1
        }, on_conflict="topic_id").execute()

    async def get_all_progress(self):
            """Recupera todo el historial de estudio del alumno."""
            client = await self.db._get_client()
            # Hacemos un JOIN con study_topics para traer los detalles del tema
            response = await client.table("user_progress") \
                .select("*, study_topics(*)") \
                .order("mastery_level", desc=True) \
                .execute()
            return response.data