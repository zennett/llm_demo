import argparse
import asyncio
import os

from openai import AsyncOpenAI

from .coordinator import AgentCoordinator
from .utils import LiveMultiPanelDisplay


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--topic",
        type=str,
        required=True,
        help="Discussion topic",
    )
    parser.add_argument(
        "--agents",
        type=int,
        required=True,
        help="Number of agents",
    )
    parser.add_argument(
        "--model", type=str, default="gpt-4o-mini", help="Model to query"
    )
    return parser.parse_args()


async def main_async() -> int:
    args = parse_args()

    if not os.getenv("OPENAI_API_KEY"):
        print("Missing OPENAI_API_KEY.")
        return 2

    if args.agents < 1 or args.agents > 7:
        print("Number of agents must be between 1 and 7")
        return 2

    client = AsyncOpenAI()
    display = LiveMultiPanelDisplay(total_agents=args.agents)
    coordinator = AgentCoordinator(
        client=client,
        model=args.model,
        topic=args.topic,
        agent_count=args.agents,
        display=display,
    )

    try:
        await coordinator.run_session()
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    return 0


def main() -> None:
    try:
        asyncio.run(main_async())
    except RuntimeError as e:
        print(f"RuntimeError occurred: {e}.")


if __name__ == "__main__":
    main()
