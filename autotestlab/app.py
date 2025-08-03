from flask import Flask, render_template, jsonify
import subprocess  # for running tests
import json
import os
from datetime import datetime

app = Flask(__name__)

HISTORY_FILE = "autotestlab/test_history.json"


@app.route("/")
def index():
    return render_template("dashboard.html")


@app.route("/run-test", methods=["POST"])
def run_test():
    try:
        # Environment and working directory info
        env = os.environ.copy()
        env["PYTHONPATH"] = os.getcwd()
        cwd = os.getcwd()

        result = subprocess.run(
            ["pytest", "autotestlab/tests/", "--maxfail=1",
             "--disable-warnings"],
            capture_output=True,
            text=True,
            cwd=cwd,
            env=env
        )
        timestamp = datetime.now().isoformat()
        test_result = {
            "timestamp": timestamp,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "status": "Passed" if result.returncode == 0 else "Failed"
        }

        # Save result
        history_file = "autotestlab/test_history.json"
        if os.path.exists(history_file):
            with open(history_file, "r") as f:
                history = json.load(f)
        else:
            history = []

        history.append(test_result)
        with open(history_file, "w") as f:
            json.dump(history, f, indent=4)
            print("===> [DEBUG] Test result saved to file.")

        return jsonify({
            "message": f"Test {test_result['status']}",
            "details": test_result["stdout"],
            "debug": result.stderr
        })

    except Exception:
        return jsonify({
            "message": f"Test {test_result['status']}",
            "details": result.stdout.replace("\x1b", ""),  # Remove ANSI codes
            "debug": result.stderr.replace("\x1b", "")
        })


@app.route("/history", methods=["GET"])
def get_history():
    try:
        history_file = "autotestlab/test_history.json"
        if os.path.exists(history_file):
            with open(history_file, "r") as f:
                history = json.load(f)
        else:
            history = []
        return jsonify(history)
    except Exception as e:
        return jsonify({"error": "Failed to read test history",
                        "details": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)  # nosec
