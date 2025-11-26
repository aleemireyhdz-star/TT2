from flask import Flask, request

app = Flask(__name__)

@app.route("/ingest", methods=["POST"])
def ingest():
    data = request.get_json(force=True, silent=True) or {}
    v = data.get("v")
    pct = data.get("pct")
    if isinstance(v, (int, float)) and isinstance(pct, (int, float)):
        print(f"v={v:.3f} V | pct={pct:.2f} %")
    else:
        print(data)
    return {"ok": True}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
    