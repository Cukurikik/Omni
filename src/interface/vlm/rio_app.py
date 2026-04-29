from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/vlm/status', methods=['GET'])
def status():
    return jsonify({"status": "running", "model": "otter-vlm-1.0"})

if __name__ == '__main__':
    app.run(port=8080)
