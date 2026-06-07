from adk import Agent, AgentConfig, tool


class SimpleAgent(Agent):
    def on_start(self, config: AgentConfig):
        print(f"SimpleAgent {config.name} started")

    def on_terminate(self):
        print(f"SimpleAgent {self.config.name} terminating")


@tool
def send_message(agent: SimpleAgent, other: SimpleAgent, text: str) -> None:
    print(f"{agent.config.name} -> {other.config.name}: {text}")
    try:
        other.handle_message(agent.config.name, {"text": text})
    except Exception:
        pass


def main():
    a1 = SimpleAgent(AgentConfig(name='agent-1'))
    a2 = SimpleAgent(AgentConfig(name='agent-2'))
    a1.register_tool('send_message', lambda other, text: send_message(a1, other, text))
    a2.register_tool('send_message', lambda other, text: send_message(a2, other, text))

    # Simulate a short chat
    a1.run()  # will run until interrupted; keep simple for example


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
