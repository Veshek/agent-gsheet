from langgraph.graph import StateGraph, MessagesState, START, END
from utils.auth import authenticate_google, list_sheets

class State:
    data: dict

def setup_langgraph():
    graph = StateGraph(State)

    # Node to authenticate user
    def auth_node(input_data): 
        sheets_service, drive_service = authenticate_google()
        return {"data":{"sheets_service": sheets_service, "drive_service": drive_service}}
    
    # Node to list sheets
    def list_sheets_node(input_data):
        drive_service = input_data['data']['drive_service']
        sheets = list_sheets(drive_service)
        return {"data":{"sheets": sheets}}

    # Add nodes to the graph
    graph.add_node("Authenticate", auth_node)
    graph.add_node("ListSheets", list_sheets_node)

    # Define flow: Authenticate -> ListSheets
    graph.add_edge("Authenticate", "ListSheets")

    return graph

graph = setup_langgraph()
graph.add_edge(START, "Authenticate")
graph.add_edge("ListSheets", END)
graph.compile()