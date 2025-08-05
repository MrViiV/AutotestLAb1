import subprocess
import os
import sys

def run_tests():
    upload_dir = "autotestlab/uploads"
    test_files = [f for f in os.listdir(upload_dir) if f.endswith(".py")]


    for filename in test_files:
        filepath = os.path.join(upload_dir, filename)
        print(f"Running tests in: {filename}")
        result = subprocess.run(
            ["pytest", filepath, "--disable-warnings"],
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print("Errors:\n", result.stderr, file=sys.stderr)


if __name__ == "__main__":
    run_tests()
