import os
import time
from datetime import datetime

import httpx

AGENT_ID = os.getenv('AGENT_ID', 'unknown')
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')
AGENT_NAME = os.getenv('AGENT_NAME', 'hello-agent')

HEARTBEAT_INTERVAL = 5


def send_heartbeat():
    try:
        with httpx.Client(timeout=5) as client:
            client.post(
                f"{BACKEND_URL}/api/agents/{AGENT_ID}/heartbeat",
                json={"status": "Running"},
            )
    except Exception:
        pass


def main():
    while True:
        print(f"[{datetime.utcnow().isoformat()}] Agent {AGENT_NAME} ({AGENT_ID}) heartbeat")
        send_heartbeat()
        time.sleep(HEARTBEAT_INTERVAL)


if __name__ == '__main__':
    main()
