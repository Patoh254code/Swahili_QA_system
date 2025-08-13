import subprocess
import time
from pyngrok import ngrok

# ===============================
# CONFIG
# ===============================
FASTAPI_FILE = "api.py"    # your FastAPI script
STREAMLIT_FILE = "ui.py"   # your Streamlit script
FASTAPI_PORT = 8000
STREAMLIT_PORT = 8501

# ===============================
# 1️⃣ Start FastAPI in background
# ===============================
print("🚀 Starting FastAPI backend...")
fastapi_proc = subprocess.Popen(
    ["uvicorn", f"{FASTAPI_FILE.replace('.py', '')}:app", "--host", "0.0.0.0", "--port", str(FASTAPI_PORT)]
)
time.sleep(3)  # give backend time to start

# ===============================
# 2️⃣ Start Streamlit in background
# ===============================
print("🚀 Starting Streamlit frontend...")
streamlit_proc = subprocess.Popen(
    ["streamlit", "run", STREAMLIT_FILE, "--server.port", str(STREAMLIT_PORT)]
)
time.sleep(5)  # give frontend time to start

# ===============================
# 3️⃣ Start ngrok for Streamlit
# ===============================
print("🌍 Starting ngrok tunnel...")
public_url = ngrok.connect(STREAMLIT_PORT)
print(f"✅ KenSwaQAChat is live at: {public_url}")

print("\nPress CTRL+C to stop.")

# Keep script running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n🛑 Shutting down...")
    fastapi_proc.terminate()
    streamlit_proc.terminate()
    ngrok.kill()
