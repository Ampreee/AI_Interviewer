import subprocess
import sys
import time
import signal


def main():
    print("Starting")
    backend_process = subprocess.Popen(
        ["uvicorn", "main:app", "--reload"],
        cwd="backend"
    )
    time.sleep(2)
    frontend_process = subprocess.Popen(
        ["streamlit", "run", "app.py"],
        cwd="frontend"
    )
    backend_process.wait()
    frontend_process.wait()
        

if __name__ == "__main__":
    main()
