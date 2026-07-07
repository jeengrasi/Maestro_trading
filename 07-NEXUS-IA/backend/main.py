from flask import Flask, request, jsonify
from db import get_connection
from datetime import datetime

app = Flask(__name__)

@app.route("/log", methods=["POST"])
def registrar_log():
    source = request.args.get("source")
    message = request.args.get("message")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO logs (timestamp, source, message) VALUES (?, ?, ?)",
        (datetime.utcnow().isoformat(), source, message)
    )
    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})

@app.route("/event", methods=["POST"])
def registrar_evento():
    tipo = request.args.get("type")
    detalle = request.args.get("description")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO eventos (timestamp, tipo, detalle) VALUES (?, ?, ?)",
        (datetime.utcnow().isoformat(), tipo, detalle)
    )
    conn.commit()
    conn.close()

    return jsonify({"status": "event_registered"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
