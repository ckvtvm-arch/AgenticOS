import argparse
import os
import runpy
import types
import subprocess
import sys
from pathlib import Path


TEMPLATE = '''from adk import Agent, tool, on_message, AgentConfig


class HelloAgent(Agent):
    def on_start(self, config: AgentConfig):
        print(f"HelloAgent starting: {config.name}")

    def on_terminate(self):
        print("HelloAgent terminating")


@tool
def echo(text: str) -> str:
    return text


@on_message
def handler(sender, payload):
    print(f"Received message from {sender}: {payload}")


if __name__ == '__main__':
    a = HelloAgent(AgentConfig(name='hello-agent'))
    a.register_tool('echo', echo)
    a.set_message_handler(handler)
    try:
        a.run()
    except KeyboardInterrupt:
        a.stop()
'''


def cmd_init(args: argparse.Namespace) -> int:
    target = Path(args.name)
    target.mkdir(parents=True, exist_ok=True)
    (target / '__init__.py').write_text('')
    (target / f"{args.name}.py").write_text(TEMPLATE)
    print(f"Scaffolded agent at {target.resolve()}")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    path = Path(args.file)
    if not path.exists():
        print(f"File not found: {path}")
        return 2
    print(f"Running agent file: {path}")
    ns = {}
    runpy.run_path(str(path), init_globals=ns)

    # Try to find an Agent instance or subclass to run with ADK wiring
    from adk import Agent, attach_decorated_to_agent

    # If module exposes an instance named 'agent' or 'a', use it
    for candidate_name in ('agent', 'a', 'AGENT'):
        candidate = ns.get(candidate_name)
        if isinstance(candidate, Agent):
            attach_decorated_to_agent(candidate, types.SimpleNamespace(**ns))
            try:
                candidate.run()
            except KeyboardInterrupt:
                candidate.stop()
            return 0

    # Otherwise, look for Agent subclasses
    for obj in ns.values():
        try:
            if isinstance(obj, type) and issubclass(obj, Agent) and obj is not Agent:
                inst = obj()
                attach_decorated_to_agent(inst, types.SimpleNamespace(**ns))
                try:
                    inst.run()
                except KeyboardInterrupt:
                    inst.stop()
                return 0
        except Exception:
            continue

    # Fallback: nothing to run as an Agent, execute as script
    runpy.run_path(str(path), run_name='__main__')
    return 0


def cmd_test(args: argparse.Namespace) -> int:
    # Run tests in a sandboxed subprocess to provide isolation and resource limits.
    cmd = [sys.executable, '-m', 'adk.sandbox', args.file, '--timeout', '10', '--mem', '200']
    print('Running sandboxed tests:', ' '.join(cmd))
    proc = subprocess.run(cmd)
    return proc.returncode


def cmd_build(args: argparse.Namespace) -> int:
    # Very small placeholder: create a zip of the directory
    import shutil
    src = Path(args.dir)
    if not src.exists():
        print(f"Directory not found: {src}")
        return 2
    out = shutil.make_archive(str(src), 'zip', root_dir=str(src))
    print(f"Built package: {out}")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(prog='agentic')
    sub = parser.add_subparsers(dest='cmd')

    p_init = sub.add_parser('init')
    p_init.add_argument('name')

    p_run = sub.add_parser('run')
    p_run.add_argument('file')

    p_test = sub.add_parser('test')
    p_test.add_argument('file')

    p_build = sub.add_parser('build')
    p_build.add_argument('dir')

    args = parser.parse_args(argv)
    if args.cmd == 'init':
        return cmd_init(args)
    if args.cmd == 'run':
        return cmd_run(args)
    if args.cmd == 'test':
        return cmd_test(args)
    if args.cmd == 'build':
        return cmd_build(args)
    parser.print_help()
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
