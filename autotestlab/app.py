from flask import Flask, render_template, jsonify
import subprocess
import json
import os
from datetime import datetime

app = Flask(__name__)
HISTORY_FILE = os.path.join(os.path.dirname(__file__), "test_history.json")


@app.route("/")
def index():
    return render_template("dashboard.html")


@app.route("/run-test", methods=["POST"])
def run_test():
    timestamp = datetime.now().isoformat()
    test_result = {
        "timestamp": timestamp,
        "returncode": None,
        "stdout": "",
        "stderr": "",
        "status": "Failed"
    }

    try:
        env = os.environ.copy()
        env["PYTHONPATH"] = os.getcwd()

        result = subprocess.run(
            ["pytest", "autotestlab/tests/", "--maxfail=1",
             "--disable-warnings"],
            capture_output=True,
            text=True,
            cwd=os.getcwd(),
            env=env
        )

        test_result["returncode"] = result.returncode
        test_result["stdout"] = result.stdout
        test_result["stderr"] = result.stderr
        test_result["status"] = (
            "Passed" if result.returncode == 0 else "Failed"
        )

        # Load existing history
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r") as f:
                try:
                    history = json.load(f)
                except json.JSONDecodeError:
                    history = []
        else:
            history = []

        # Append and write
        history.append(test_result)
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=4)

        return jsonify({
            "message": f"Test {test_result['status']}",
            "details": test_result["stdout"],
            "debug": test_result["stderr"]
        })

    except Exception as e:
        return jsonify({
            "message": "Error during test execution",
            "error": str(e),
            "details": test_result["stdout"],
            "debug": test_result["stderr"]
        }), 500


@app.route("/history", methods=["GET"])
def get_history():
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r") as f:
                history = json.load(f)
        else:
            history = []
        return jsonify(history)
    except Exception as e:
        return jsonify({"error": "Failed to read test history",
                        "details": str(e)}), 500


@app.route("/clear-history", methods=["DELETE"])
def clear_history():
    try:
        history_file = "autotestlab/test_history.json"
        if os.path.exists(history_file):
            with open(history_file, "w") as f:
                json.dump([], f)  # Overwrite with empty list
        return jsonify({"message": "History cleared"}), 200
    except Exception as e:
        return jsonify({"error": "Failed to clear history",
                        "details": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)  # nosec
