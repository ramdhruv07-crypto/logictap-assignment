import os
import sqlite3

from flask import Flask, jsonify, request

DB_PATH = os.environ.get("CALLS_DB", "calls.db")


def get_db(path=DB_PATH):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """CREATE TABLE IF NOT EXISTS calls (
               call_id TEXT PRIMARY KEY,
               status TEXT NOT NULL,
               duration_secs INTEGER
           )"""
    )
    return conn


def create_app(db_path=DB_PATH):
    app = Flask(__name__)
    app.config["DB_PATH"] = db_path
    get_db(db_path).close()  # make sure the table exists

    @app.route("/call-ended", methods=["POST"])
    def call_ended():
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"error": "body must be a JSON object"}), 400

        call_id = data.get("call_id")
        if not isinstance(call_id, str) or not call_id.strip():
            return jsonify({"error": "call_id is required and must be a non-empty string"}), 400

        status = data.get("status")
        if not isinstance(status, str) or not status:
            return jsonify({"error": "status is required and must be a string"}), 400

        duration = data.get("duration_secs")
        if duration is not None and (isinstance(duration, bool) or not isinstance(duration, int) or duration < 0):
            return jsonify({"error": "duration_secs must be a non-negative integer"}), 400

        conn = get_db(app.config["DB_PATH"])
        try:
            # The PRIMARY KEY makes the duplicate check atomic: no race between
            # "does it exist?" and "insert it".
            cur = conn.execute(
                "INSERT OR IGNORE INTO calls (call_id, status, duration_secs) VALUES (?, ?, ?)",
                (call_id, status, duration),
            )
            conn.commit()
            created = cur.rowcount == 1
        finally:
            conn.close()

        if created:
            return jsonify({"message": "stored", "call_id": call_id}), 201
        return jsonify({"message": "already received", "call_id": call_id, "duplicate": True}), 200

    @app.route("/calls/<call_id>", methods=["GET"])
    def get_call(call_id):
        conn = get_db(app.config["DB_PATH"])
        try:
            row = conn.execute("SELECT * FROM calls WHERE call_id = ?", (call_id,)).fetchone()
        finally:
            conn.close()
        if row is None:
            return jsonify({"error": f"no call found with call_id '{call_id}'"}), 404
        return jsonify(dict(row))

    return app


if __name__ == "__main__":
    create_app().run(port=5000)
