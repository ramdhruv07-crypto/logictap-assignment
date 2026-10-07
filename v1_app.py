from flask import Flask, request, jsonify

app = Flask(__name__)

calls = {}


@app.route("/call-ended", methods=["POST"])
def call_ended():
    data = request.get_json()
    call_id = data["call_id"]
    calls[call_id] = {
        "call_id": call_id,
        "status": data["status"],
        "duration_secs": data["duration_secs"],
    }
    return jsonify({"message": "stored"}), 200


@app.route("/calls/<call_id>", methods=["GET"])
def get_call(call_id):
    if call_id not in calls:
        return jsonify({"error": "not found"}), 404
    return jsonify(calls[call_id])


if __name__ == "__main__":
    app.run(port=5000)
