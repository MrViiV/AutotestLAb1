import json
from datetime import datetime

sample = [{
    "timestamp": datetime.now().isoformat(),
    "returncode": 0,
    "stdout": "Test passed.",
    "stderr": "",
    "status": "Passed"
}]

with open("autotestlab/test_history.json", "w") as f:
    json.dump(sample, f, indent=4)
