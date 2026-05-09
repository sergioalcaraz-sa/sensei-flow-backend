# app/agents/graph.py
from langgraph.graph import StateGraph, END
from app.agents.state import AgentState
from app.services.ai_service import AIService
from app.services.database import DatabaseService
from fastapi import HTTPException

class JapaneseOrchestrator:
    def __init__(self):
        self.ai_service = AIService()
        self.db_service = DatabaseService() # Instanciamos el nuevo servicio
        
        workflow = StateGraph(AgentState)
        
        # Definir nodos
        workflow.add_node("analyze_linguistics", self.analyze_linguistics)
        workflow.add_node("persist_data", self.persist_data) # Nuevo nodo
        
        # Definir el flujo: Entrada -> Análisis -> Base de Datos -> Fin
        workflow.set_entry_point("analyze_linguistics")
        workflow.add_edge("analyze_linguistics", "persist_data")
        workflow.add_edge("persist_data", END)
        
        self.app = workflow.compile()

    async def analyze_linguistics(self, state: AgentState):
        try:
            result = await self.ai_service.analyze_text(state["input_text"])
            # Actualizamos el estado con el análisis
            return {"analysis": result}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error en IA: {str(e)}")

    async def persist_data(self, state: AgentState):
        try:
            # Obtenemos el análisis del estado y lo guardamos
            analysis_data = state["analysis"]
            await self.db_service.save_analysis(analysis_data)
            # No necesitamos modificar el estado para la salida
            return {} 
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error en BD: {str(e)}")

orchestrator = JapaneseOrchestrator()