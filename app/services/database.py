# app/services/database.py
from supabase import create_async_client, AsyncClient
from app.core.config import settings
from app.schemas.analysis import JapaneseAnalysisResponse
from fastapi import HTTPException

class DatabaseService:
    def __init__(self):
        # Eliminamos la inicialización síncrona aquí
        pass

    async def _get_client(self) -> AsyncClient:
        """Inicializador asíncrono (Lazy Load) del cliente de Supabase."""
        return await create_async_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY
        )

    async def save_analysis(self, analysis: JapaneseAnalysisResponse):
        """Persiste el análisis en Supabase."""
        try:
            # 1. Esperamos la conexión real
            client = await self._get_client()
            
            # 2. Serializamos forzando JSON para compatibilidad con Supabase
            data = {
                "original_text": analysis.original_text,
                "tokens": [token.model_dump(mode='json') for token in analysis.tokens],
                "grammar_note": analysis.grammar_note
            }
            
            # 3. Insertamos usando upsert para evitar errores de duplicidad
            response = await client.table("japanese_analyses").upsert(
                data, 
                on_conflict="original_text"
            ).execute()
            
            return response.data
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Real de Supabase: {str(e)}")

    async def get_recent_analyses(self, limit: int = 10):
        """Recupera los análisis más recientes de la base de datos."""
        try:
            client = await self._get_client()
            # Consulta SQL equivalente: SELECT * FROM japanese_analyses ORDER BY created_at DESC LIMIT X
            response = await client.table("japanese_analyses") \
                .select("*") \
                .order("created_at", desc=True) \
                .limit(limit) \
                .execute()
            
            return response.data
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error leyendo de Supabase: {str(e)}")