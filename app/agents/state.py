# app/agents/state.py
from typing import Annotated, TypedDict, List
from operator import add
from app.schemas.analysis import JapaneseAnalysisResponse

class AgentState(TypedDict):
    # El historial de mensajes o el texto de entrada
    input_text: str
    # La respuesta estructurada que iremos construyendo
    analysis: JapaneseAnalysisResponse
    # Un log de errores para reintentos lógicos
    errors: Annotated[List[str], add]