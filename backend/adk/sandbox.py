"""Simple sandbox runner for executing agent test files with resource limits.

This is intentionally small: it sets soft resource limits and executes the
target file, then runs any functions named `test_*` found in the module
namespace. It returns a non-zero exit code on failures.
"""
from __future__ import annotations

import argparse
import runpy
import signal
import sys

try:
    import resource
except Exception:
    resource = None


def _timeout_handler(signum, frame):
    raise TimeoutError("Execution timed out")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog='adk.sandbox')
    parser.add_argument('file')
    parser.add_argument('--timeout', type=int, default=10, help='CPU/time limit in seconds')
    parser.add_argument('--mem', type=int, default=200, help='Memory limit in MB')
    args = parser.parse_args(argv)

    if resource is not None:
        try:
            # CPU time
            resource.setrlimit(resource.RLIMIT_CPU, (args.timeout, args.timeout + 1))
            # Address space (virtual memory)
            mem_bytes = args.mem * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (mem_bytes, mem_bytes))
        except Exception:
            pass

    signal.signal(signal.SIGALRM, _timeout_handler)
    signal.alarm(args.timeout + 1)

    try:
        ns: dict = {}
        runpy.run_path(args.file, init_globals=ns)

        tests = [v for k, v in ns.items() if callable(v) and k.startswith('test_')]
        if not tests:
            print('No tests found')
            return 1

        failures = 0
        for t in tests:
            try:
                t()
                print(f'PASS: {t.__name__}')
            except Exception as e:
                failures += 1
                print(f'FAIL: {t.__name__} -> {e}')

        return failures
    except TimeoutError:
        print('Timed out')
        return 124
    except Exception as e:
        print('Error while running tests:', e)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
