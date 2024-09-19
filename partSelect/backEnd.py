from flask import Flask, request, jsonify
from flask_cors import CORS
from agent.agent import Agent
app = Flask(__name__)
CORS(app)
agent = Agent()
print("created Agent")

@app.route('/invoke_agent', methods=['POST'])
def invoke_agent():
    data = request.json
    input_string = data['string']
    agentOutput = agent.run(input=input_string)
    return jsonify({"response": agentOutput['output']})

if __name__ == '__main__':
    app.run(debug=False)
