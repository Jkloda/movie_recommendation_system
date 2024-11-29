from graphviz import Digraph

# Create a new directed graph for the flowchart
flowchart = Digraph(format="png")
flowchart.attr(rankdir='TB', size='8,10')

# Define nodes for the flowchart
flowchart.node("Start", "Start", shape="oval")
flowchart.node("Login", "Login", shape="diamond")
flowchart.node("Register", "Register", shape="parallelogram")
flowchart.node("SavePreferences", "Save Preferences", shape="rectangle")
flowchart.node("Database", "Database", shape="cylinder")
flowchart.node("ModelTraining", "Model Training", shape="rectangle")
flowchart.node("GenerateRec", "Generate Recommendations", shape="rectangle")
flowchart.node("End", "End", shape="oval")

# Define edges
flowchart.edge("Start", "Login")
flowchart.edge("Login", "Register", label="No")
flowchart.edge("Register", "SavePreferences")
flowchart.edge("SavePreferences", "Database")
flowchart.edge("Database", "ModelTraining")
flowchart.edge("ModelTraining", "GenerateRec", label="Load recmodel")
flowchart.edge("GenerateRec", "End")

# Additional edges for alternate paths
flowchart.edge("Login", "ModelTraining", label="Yes")

# Render and save
file_path = "./flowchart"
flowchart.render(file_path, format='png', cleanup=True)

print(f"Flowchart saved as: {file_path}.png")