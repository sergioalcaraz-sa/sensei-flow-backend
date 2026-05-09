from langchain_groq import ChatGroq
from app.schemas.analysis import JapaneseAnalysisResponse
from app.core.config import settings

class AIService:
    def __init__(self):
        self.llm = ChatGroq(
            temperature=0,
            model_name="llama-3.3-70b-versatile", # O modelo similar en Groq
            groq_api_key=settings.GROQ_API_KEY
        )

    async def analyze_text(self, text: str) -> JapaneseAnalysisResponse:
            structured_llm = self.llm.with_structured_output(JapaneseAnalysisResponse)
            
            # CAMBIO CRÍTICO: Prompt de nivel ingeniería
            prompt = f"""
    Eres un lingüista experto en japonés. Analiza el siguiente texto: "{text}"

    Reglas estrictas para el análisis de tokens:
    1. Divide la oración en tokens lógicos (palabras, partículas, verbos conjugados).
    2. El campo 'reading' es OBLIGATORIO para cada token.
    - Si es Kanji: escribe su lectura en Hiragana.
    - Si es Katakana: escribe su equivalente en Hiragana.
    - Si ya es Hiragana: repite el Hiragana.
    - NUNCA dejes el campo 'reading' vacío o en null.
    3. El campo 'meaning' debe ser preciso en español.
            """
            
            response = await structured_llm.ainvoke(prompt)
            return response