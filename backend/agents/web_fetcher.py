import time
import httpx
from adk import Agent, AgentConfig, tool


class WebFetcherAgent(Agent):
    def on_start(self, config: AgentConfig):
        print(f"WebFetcherAgent started: {config.name}")

    def on_terminate(self):
        print("WebFetcherAgent terminating")


_LAST_CALL = 0.0
_MIN_INTERVAL = 0.5


@tool
def fetch_url(url: str) -> str:
    global _LAST_CALL
    now = time.time()
    elapsed = now - _LAST_CALL
    if elapsed < _MIN_INTERVAL:
        time.sleep(_MIN_INTERVAL - elapsed)
    _LAST_CALL = time.time()
    with httpx.Client(timeout=10) as client:
        r = client.get(url)
        r.raise_for_status()
        return r.text


if __name__ == '__main__':
    a = WebFetcherAgent(AgentConfig(name='web-fetcher'))
    a.register_tool('fetch_url', fetch_url)
    try:
        a.run()
    except KeyboardInterrupt:
        a.stop()
