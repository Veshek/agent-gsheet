from langgraph import Graph
from auth import authenticate_google, list_sheets

def setup_langgraph():
    graph = Graph()

    # Node to authenticate user
    def auth_node(input_data):
        sheets_service, drive_service = authenticate_google()
        return {"sheets_service": sheets_service, "drive_service": drive_service}
    
    # Node to list sheets
    def list_sheets_node(input_data):
        drive_service = input_data['drive_service']
        sheets = list_sheets(drive_service)
        return {"sheets": sheets}

    # Add nodes to the graph
    graph.add_node("Authenticate", auth_node)
    graph.add_node("ListSheets", list_sheets_node)

    # Define flow: Authenticate -> ListSheets
    graph.add_edge("Authenticate", "ListSheets")

    return graph

# Running the graph
graph = setup_langgraph()
output = graph.run({})
print(output)