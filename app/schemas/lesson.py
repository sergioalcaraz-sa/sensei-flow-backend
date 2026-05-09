# app/schemas/lesson.py
from pydantic import BaseModel, Field
from typing import List

class LessonExample(BaseModel):
    japanese: str = Field(..., description="Frase de ejemplo usando KANJI y KANA reales (Ej: 私はりんごを食べた). PROHIBIDO ROMAJI.")
    reading: str = Field(..., description="Lectura fonética exclusivamente en puro HIRAGANA (Ej: わたしはりんごをたべた). PROHIBIDO ROMAJI.")
    spanish: str = Field(..., description="Traducción al español")

class LessonContent(BaseModel):
    topic_title: str
    explanation: str = Field(..., description="Explicación gramatical o lingüística profunda")
    examples: List[LessonExample] = Field(..., max_items=3)
    key_points: List[str] = Field(..., description="Puntos clave para recordar")
    jlpt_level: str