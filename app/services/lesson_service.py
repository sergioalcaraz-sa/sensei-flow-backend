# app/services/lesson_service.py
from langchain_groq import ChatGroq
from app.schemas.lesson import LessonContent
from app.core.config import settings

class LessonService:
    def __init__(self):
        self.llm = ChatGroq(
            temperature=0.3,
            model_name="llama-3.3-70b-versatile",
            groq_api_key=settings.GROQ_API_KEY
        )

    async def generate_lesson(self, topic: dict) -> LessonContent:
        structured_llm = self.llm.with_structured_output(LessonContent)
        
        prompt = f"""
        Actúa como un Sensei de japonés universitario muy exigente. 
        Crea una lección EXHAUSTIVA y PROFUNDA para el tema: "{topic['title']}" (Nivel {topic['jlpt_level']}).
        La explicación debe ser detallada, cubriendo matices lingüísticos, excepciones a la regla y contexto nativo de uso real. 
        No te quedes en lo básico. Incluye ejemplos variados y puntos clave críticos.
        
        REGLAS CRÍTICAS DE FORMATO (¡CUMPLE ESTRICTAMENTE!):
        1. CERO RŌMAJI: Está TOTALMENTE PROHIBIDO usar alfabeto latino (rōmaji) para escribir palabras japonesas en toda la lección.
        2. CAMPO 'japanese': DEBE escribirse usando escritura japonesa nativa (Kanji, Hiragana, Katakana). Ejemplo correcto: 私は映画を見た。
        3. CAMPO 'reading': DEBE contener exclusivamente la lectura en HIRAGANA. Ejemplo correcto: わたしはえいがをみた。
        """
        
        return await structured_llm.ainvoke(prompt)