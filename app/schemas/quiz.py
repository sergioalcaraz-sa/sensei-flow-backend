# app/schemas/quiz.py
from pydantic import BaseModel, Field
from typing import List

class QuizOption(BaseModel):
    id: str = Field(..., description="Letra de la opción (A, B, C, D)")
    text: str = Field(..., description="El texto de la opción")

class QuizQuestion(BaseModel):
    thought_process: str = Field(..., description="Piensa paso a paso: 1. ¿Estoy evaluando estrictamente el tema pedido? 2. Si es de rellenar huecos, ¿el hueco corresponde exactamente a la respuesta sin contradecir el texto visible?")
    question_text: str = Field(..., description="La pregunta en español.")
    options: List[QuizOption] = Field(..., description="Exactamente 4 opciones.")
    correct_option_id: str = Field(..., description="ID correcto (ej. 'A').")
    explanation: str = Field(..., description="Explicación de la respuesta.")

class TopicQuiz(BaseModel):
    questions: List[QuizQuestion] = Field(..., description="Exactamente 6 preguntas variadas y de alta dificultad.")