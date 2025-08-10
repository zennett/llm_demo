import asyncio
from typing import Dict, Set

from rich.columns import Columns
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

RICH_COLORS = ["cyan", "magenta", "yellow", "green", "blue", "red", "white"]


class LiveMultiPanelDisplay:
    """
    A terminal UI that keeps each agent's response in a separate colored panel
    and updates all of them concurrently as tokens arrive.

    Panel title: Name (Age, Occupation, Personality)
    Panel border color: consistent per agent
    """

    def __init__(self, total_agents: int) -> None:
        self.total_agents = total_agents
        self.buffers: Dict[int, str] = {}
        self.names: Dict[int, str] = {}  # Display name with age & personality
        self.ended: Set[int] = set()
        self._update_event: asyncio.Event = asyncio.Event()
        self.colors: Dict[int, str] = {}

    def register_agent(self, agent_index: int, display_name: str) -> None:
        """
        Register the display name for an agent, and assign a consistent color.
        Expected format from caller: "Name (Age, Personality)"
        """
        self.buffers.setdefault(agent_index, "")
        self.names[agent_index] = display_name
        self.colors[agent_index] = RICH_COLORS[agent_index % len(RICH_COLORS)]

    async def publish_token(self, agent_index: int, token: str) -> None:
        self.buffers[agent_index] = self.buffers.get(agent_index, "") + token
        self._update_event.set()

    async def end_agent(self, agent_index: int) -> None:
        self.ended.add(agent_index)
        self._update_event.set()

    async def fail_agent(self, agent_index: int, message: str) -> None:
        self.buffers[agent_index] = self.buffers.get(agent_index, "") + message
        await self.end_agent(agent_index)

    def _render(self):
        panels = []
        for i in sorted(self.names.keys()):
            title = f"[bold]{self.names[i]}[/bold]"
            body = self.buffers.get(i, "")
            footer = "done" if i in self.ended else "streaming…"
            panels.append(
                Panel(
                    Text(body),
                    title=title,
                    subtitle=footer,
                    border_style=self.colors.get(i, "white"),
                    padding=(1, 1),
                )
            )
        return Columns(panels, equal=True, expand=True)

    async def run(self) -> None:
        refresh_hz = 20
        refresh_dt = 1.0 / refresh_hz
        with Live(
            self._render(), refresh_per_second=refresh_hz, transient=False
        ) as live:
            while len(self.ended) < self.total_agents:
                try:
                    await asyncio.wait_for(
                        self._update_event.wait(), timeout=refresh_dt
                    )
                except asyncio.TimeoutError:
                    pass
                self._update_event.clear()
                live.update(self._render())
