from flask import Flask, request, jsonify  # type: ignore

app = Flask(__name__)

@app.route('/api/', methods=['GET'])
def get_greeting():
    message = {"message": "Hello from the Flask server!"}
    return jsonify(message)
    
@app.route('/api/snake/', methods=['POST'])
def receive_data():
    if request.method == 'POST':
        data = request.get_json()
        # Process the data (e.g., save to a database, perform calculations)
        response = {'message': 'Data received successfully', 'received_data': data}
        return jsonify(response), 201
    else:
        return jsonify({'error': 'Method not allowed'}), 405

if __name__ == '_main_':
    app.run(debug=True, port=5001)