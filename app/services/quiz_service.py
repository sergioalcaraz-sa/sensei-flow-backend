# app/services/quiz_service.py
from langchain_groq import ChatGroq
from app.schemas.quiz import QuizQuestion, TopicQuiz
from app.core.config import settings
from app.services.database import DatabaseService
from fastapi import HTTPException
import random

class QuizService:
    def __init__(self, db_service: DatabaseService):
        self.db = db_service
        self.llm = ChatGroq(
            temperature=0.4, # Un poco de temperatura para creatividad en los distractores
            model_name="llama-3.3-70b-versatile",
            groq_api_key=settings.GROQ_API_KEY
        )

    async def generate_quiz_from_history(self) -> QuizQuestion:
        """Obtiene un análisis reciente y genera una pregunta sobre él."""
        try:
            # 1. Recuperar contexto de la base de datos
            history = await self.db.get_recent_analyses(limit=10)
            if not history:
                raise ValueError("No hay suficiente historial para generar un examen.")
            
            # Elegimos un registro al azar de los últimos 10
            target_record = random.choice(history)
            
            # 2. Configurar el LLM estructurado
            structured_llm = self.llm.with_structured_output(QuizQuestion)
            
            # 3. Prompt de Ingeniería Pedagógica
            prompt = f"""
Eres Sensei-Flow, un tutor estricto pero amable de japonés.
Tu alumno estudió recientemente esta frase: "{target_record['original_text']}"
El análisis que se le dio fue: {target_record['tokens']}

Tu tarea: Genera UNA pregunta de opción múltiple (4 opciones) para evaluar si el alumno recuerda una palabra clave, su lectura en Hiragana, o el concepto gramatical de esa frase específica.

Reglas:
1. Las opciones incorrectas (distractores) deben ser plausibles pero claramente falsas para un estudiante que prestó atención.
2. Explica claramente la respuesta en el campo 'explanation'.
"""
            # 4. Generación asíncrona
            quiz = await structured_llm.ainvoke(prompt)
            return quiz

        except ValueError as ve:
            raise HTTPException(status_code=400, detail=str(ve))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generando quiz: {str(e)}")

    async def generate_topic_quiz(self, topic: dict) -> TopicQuiz:
        """Genera una batería de 6 preguntas estrictamente ligadas al tema."""
        try:
            structured_llm = self.llm.with_structured_output(TopicQuiz)
            
            prompt = f"""
            Eres el examinador más estricto y preciso del JLPT {topic['jlpt_level']}.
            
            TEMA ÚNICO Y EXCLUSIVO A EVALUAR: "{topic['title']}"
            DESCRIPCIÓN DEL TEMA: {topic['description']}
            
            Tu tarea es generar un TEST DE EXACTAMENTE 6 PREGUNTAS.
            
            REGLAS CRÍTICAS DE CALIDAD (DEBES CUMPLIRLAS TODAS):
            1. USO OBLIGATORIO DEL JAPONÉS: Las oraciones y textos que el alumno debe analizar DEBEN estar en JAPONÉS. Las instrucciones de la pregunta irán en español, pero el material de evaluación es japonés.
               - EJEMPLO CORRECTO: "¿Qué partícula falta en la frase: 私___りんごを食べます?"
               - EJEMPLO INCORRECTO: "¿Qué opción completa: Yo ____ un libro?" (¡Prohibido hacer exámenes de español!).
            2. RELEVANCIA ABSOLUTA: Las 6 preguntas DEBEN evaluar DIRECTA Y ÚNICAMENTE el tema "{topic['title']}".
            3. COHERENCIA ESTRUCTURAL: 
               - Si usas el formato de "rellenar el hueco" (____), asegúrate de que la respuesta no esté ya escrita en la pregunta.
               - Las opciones (A, B, C, D) deben ser elementos en japonés (ej. diferentes partículas o conjugaciones) o traducciones literales, según corresponda.
            4. VARIEDAD DE FORMATOS:
               - ¿Qué opción completa correctamente la frase en japonés?
               - ¿Cuál es la traducción correcta de esta oración japonesa?
               - ¿Qué frase en japonés utiliza correctamente este concepto?
            5. TRAMPAS LÓGICAS: Los distractores deben ser errores gramaticales comunes en estudiantes de japonés.

            Usa el campo 'thought_process' en cada pregunta para auditar tu propio trabajo: "1. ¿La frase a evaluar está en japonés? 2. ¿Evalúa exactamente el tema pedido?".
            """
            return await structured_llm.ainvoke(prompt)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generando examen: {str(e)}")