from typing import Dict, List

from openai import AsyncOpenAI

from . import storage
from .utils import LiveMultiPanelDisplay

AGENT_SYSTEM_TEMPLATE = (
    "You are the following persona providing your own personal thoughts, "
    "feelings, and perspective on a specific topic.\n\n"
    "Name: {name}\n"
    "Age: {age}\n"
    "Occupation: {occupation}\n"
    "Personality: {personality}\n\n"
    "Stay fully in character. Base your response on this persona's life "
    "experience, values, and worldview.\n"
    "Be concise but offer substance. Avoid generic statements.\n"
)

AGENT_USER_TEMPLATE = (
    'Topic: "{topic}"\n\n'
    "Share your personal thoughts and feelings on this topic from your "
    "perspective.\n"
    "Aim for 2-4 sentences. Do not include your name; it will be shown "
    "externally.\n"
)


class Agent:
    def __init__(
        self,
        agent_index: int,
        model: str,
        profile: Dict,
        client: AsyncOpenAI,
        display: LiveMultiPanelDisplay,
        topic: str,
        agent_count: int,
    ) -> None:
        self.i = agent_index
        self.model = model
        self.profile = profile
        self.client = client
        self.display = display
        self.topic = topic
        self.agent_count = agent_count

    async def send_message(self) -> None:
        title = (
            f"{self.profile['name']} "
            f"({self.profile['age']}, {self.profile['occupation']}, "
            f"{self.profile['personality']})"
        )
        self.display.register_agent(self.i, title)

        messages = [
            {
                "role": "system",
                "content": AGENT_SYSTEM_TEMPLATE.format(**self.profile),
            },
            {
                "role": "user",
                "content": AGENT_USER_TEMPLATE.format(topic=self.topic),
            },
        ]

        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=300,
                stream=True,
            )
        except Exception as e:
            await self.display.fail_agent(
                self.i,
                f"[error] stream failed: {e}",
            )
            return

        collected: List[str] = []
        try:
            async for chunk in stream:
                delta = chunk.choices[0].delta
                token = delta.content or ""
                if token:
                    collected.append(token)
                    await self.display.publish_token(self.i, token)
        finally:
            await self.display.end_agent(self.i)

        response = "".join(collected).strip()
        if response:
            storage.append_message(
                self.topic,
                self.profile["name"],
                self.profile["age"],
                self.profile["occupation"],
                self.profile["personality"],
                response,
            )
