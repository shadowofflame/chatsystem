"""
Simple LangGraph STDIO runner.
Reads user input from STDIN and outputs agent replies to STDOUT.
"""

import argparse
import sys

from langgraph_agent import LangGraphAgent


def main() -> None:
    parser = argparse.ArgumentParser(description="LangGraph STDIO entrypoint with deep thinking support")
    parser.add_argument("--workspace", default="./workspace", help="Workspace directory for file operations")
    parser.add_argument("--memory", default="./chat_memory_db", help="Memory persistence directory")
    parser.add_argument("--model", default="deepseek-chat", help="Model name")
    parser.add_argument("--deep", action="store_true", help="Enable deep thinking (Tree-of-Thought)")
    parser.add_argument("--branches", type=int, default=3, help="Thought branches")
    parser.add_argument("--depth", type=int, default=2, help="Thought depth")
    args = parser.parse_args()

    agent = LangGraphAgent(
        model=args.model,
        memory_dir=args.memory,
        workspace_dir=args.workspace,
        default_branches=args.branches,
        default_depth=args.depth,
    )

    sys.stdout.write("LangGraph STDIO ready. Type your message and press Enter.\n")
    sys.stdout.flush()

    for line in sys.stdin:
        message = line.strip()
        if not message:
            continue
        try:
            reply = agent.chat(
                message,
                deep_think=args.deep,
                max_branches=args.branches,
                max_depth=args.depth,
            )
        except Exception as exc:  # pragma: no cover
            reply = f"error: {exc}"
        sys.stdout.write(reply + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
