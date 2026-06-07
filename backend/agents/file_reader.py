import os
from pathlib import Path
from adk import Agent, AgentConfig, tool


class FileReaderAgent(Agent):
    def on_start(self, config: AgentConfig):
        print(f"FileReaderAgent started: {config.name}")

    def on_terminate(self):
        print("FileReaderAgent terminating")


@tool
def read_file(path: str) -> str:
    # Simple permission check: only allow files under current working directory
    base = Path(os.getcwd()).resolve()
    target = (base / path).resolve()
    if not str(target).startswith(str(base)):
        raise PermissionError("Access denied")
    if not target.exists():
        raise FileNotFoundError(path)
    return target.read_text()


if __name__ == '__main__':
    a = FileReaderAgent(AgentConfig(name='file-reader'))
    a.register_tool('read_file', read_file)
    try:
        a.run()
    except KeyboardInterrupt:
        a.stop()
