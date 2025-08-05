from flask import Flask, render_template, jsonify, request
import subprocess
import json
import os
import re
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
HISTORY_FILE = os.path.join(os.path.dirname(__file__), "test_history.json")
UPLOAD_FOLDER = "autotestlab/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def extract_test_stats(stdout: str):
    """Extract number of passed/failed tests from pytest output"""
    passed = failed = 0
    match = re.search(r"=+.*?(\d+)\s+failed.*?(\d+)\s+passed.*?=+",
                      stdout, re.IGNORECASE)
    if match:
        failed = int(match.group(1))
        passed = int(match.group(2))
    else:
        match_pass = re.search(r"=+.*?(\d+)\s+passed.*?=+",
                               stdout, re.IGNORECASE)
        match_fail = re.search(r"=+.*?(\d+)\s+failed.*?=+",
                               stdout, re.IGNORECASE)
        if match_pass:
            passed = int(match_pass.group(1))
        if match_fail:
            failed = int(match_fail.group(1))
    status = "Passed" if failed == 0 else "Failed"
    return status, passed, failed


@app.route("/")
def index():
    return render_template("dashboard.html")


@app.route("/run-test", methods=["POST"])
def run_test():
    timestamp = datetime.now().isoformat()

    try:
        env = os.environ.copy()
        env["PYTHONPATH"] = os.getcwd()

        result = subprocess.run(
            ["pytest", "autotestlab/tests/", "--disable-warnings"],
            capture_output=True,
            text=True,
            cwd=os.getcwd(),
            env=env
        )

        status, passed, failed = extract_test_stats(result.stdout)

        test_result = {
            "timestamp": timestamp,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "status": status,
            "passed": passed,
            "failed": failed
        }

        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r") as f:
                history = json.load(f)
        else:
            history = []

        history.append(test_result)
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=4)

        return jsonify({
            "message": f"Test {status}",
            "details": result.stdout,
            "debug": result.stderr,
            "passed": passed,
            "failed": failed
        })

    except Exception as e:
        return jsonify({
            "message": "Error during test execution",
            "error": str(e),
            "details": "",
            "debug": ""
        }), 500


@app.route("/upload-test", methods=["POST"])
def upload_test():
    if "file" not in request.files:
        return jsonify({"message": "No file uploaded."}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"message": "No file selected."}), 400

    if not file.filename.endswith(".py"):
        return jsonify({"message": "Only .py files allowed."}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    try:
        result = subprocess.run(
            ["pytest", filepath, "--disable-warnings"],
            capture_output=True,
            text=True,
            cwd=os.getcwd(),
            env={**os.environ, "PYTHONPATH": os.getcwd()}
        )

        timestamp = datetime.now().isoformat()
        status, passed, failed = extract_test_stats(result.stdout)

        test_result = {
            "timestamp": timestamp,
            "filename": filename,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "status": status,
            "passed": passed,
            "failed": failed
        }

        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r") as f:
                history = json.load(f)
        else:
            history = []

        history.append(test_result)
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=4)

        return jsonify({
            "message": f"Uploaded Test {status}",
            "details": result.stdout,
            "passed": passed,
            "failed": failed
        })

    except Exception as e:
        return jsonify({"message": "Upload failed", "error": str(e)}), 500


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
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "w") as f:
                json.dump([], f)
        return jsonify({"message": "History cleared"}), 200
    except Exception as e:
        return jsonify({"error": "Failed to clear history",
                        "details": str(e)}), 500


@app.route("/view-test/<filename>")
def view_test(filename):
    filepath = os.path.join(UPLOAD_FOLDER, secure_filename(filename))
    if not os.path.exists(filepath):
        return "File not found", 404
    with open(filepath, "r") as f:
        content = f.read()
    return f"<pre>{content}</pre>"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
