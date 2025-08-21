
import subprocess
import time
from datetime import datetime, timedelta

# Endpoints in your FastAPI app
ENDPOINTS = [
    "/brands",
    "/categories",
    "/flash-sales",
    "/sneakers",
    "/stats"
]

SERVER = "localhost"
PORT = 8000

# Baseline load
BASE_RATE = 200    # requests/sec
BASE_CONNS = 50

# Spike load (only for /checkout)
SPIKE_RATE = 20000   # requests/sec
SPIKE_CONNS = 100
SPIKE_DURATION = 300  # seconds (~5 minutes)

# Spike times for checkout (24h)
CHECKOUT_ENDPOINT = "/checkout"
CHECKOUT_SPIKE_HOURS = [4, 8, 10, 12, 14, 18, 20, 23]

def run_httperf(uri, rate, conns):
    cmd = [
        "httperf",
        f"--server={SERVER}",
        f"--port={PORT}",
        f"--uri={uri}",
        f"--rate={rate}",
        f"--num-conns={conns}",
        "--num-calls=1",
        "--timeout=5"
    ]
    print(f"🚀 Running: {uri} @ {rate} req/s, {conns} conns")
    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print("⚠️ httperf error:", e.stderr.decode())

def main():
    start = datetime.now()
    end = start + timedelta(hours=24)

    while datetime.now() < end:
        now = datetime.now()
        hour, minute = now.hour, now.minute

        for endpoint in ENDPOINTS:
            run_httperf(endpoint, BASE_RATE, BASE_CONNS)

        # Check if we're in a spike window for /checkout
        if hour in CHECKOUT_SPIKE_HOURS and minute < 5:
            run_httperf(CHECKOUT_ENDPOINT, SPIKE_RATE, SPIKE_CONNS)

        time.sleep(40)  # slight stagger

if __name__ == "__main__":
    main()
