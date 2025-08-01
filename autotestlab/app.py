from flask import Flask, render_template, jsonify
import time  # optional for simulating delay

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("dashboard.html")


@app.route("/run-test", methods=["POST"])
def run_test():
    try:
        # Simulate running a test
        time.sleep(2)  # Optional: simulate a delay
        return jsonify({"message": "Test completed successfully!"}), 200
    except Exception:
        return jsonify({"message": "Error running test"}), 500
    

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000) # nosec

