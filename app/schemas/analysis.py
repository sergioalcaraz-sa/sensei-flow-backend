from pydantic import BaseModel, Field
from typing import List, Optional

class TokenAnalysis(BaseModel):
    surface: str = Field(..., description="El texto original en japonés")
    reading: str = Field(None, description="Lectura en Hiragana/Katakana")
    meaning: str = Field(..., description="Traducción al español")
    part_of_speech: str = Field(..., description="Categoría gramatical")

class JapaneseAnalysisResponse(BaseModel):
    original_text: str
    tokens: List[TokenAnalysis]
    grammar_note: Optional[str] = Field(None, description="Explicación de la estructura gramatical")