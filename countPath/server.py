from flask import Flask, request, jsonify
from threading import Thread
from flask_cors import CORS
from findRoute import findRoute
app = Flask(__name__)
CORS(app)


@app.route('/dest', methods=['POST'])
def dest():
    print('Destination received')
    print(request.json['dest'])

    route = findRoute(request.json['dest'])
    response_data = {
        'route': route
    }
    return jsonify(response_data), 200


if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5500)
