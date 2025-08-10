import asyncio
import json
from typing import Dict, List

from openai import AsyncOpenAI

from .agents import Agent
from .utils import LiveMultiPanelDisplay

PROFILE_SYSTEM = (
    "You are an expert character creator who designs diverse, realistic "
    "personas that will share unique views, thoughts, and feelings on a "
    "topic. Output must be STRICT JSON following the schema."
)

PROFILE_USER_TEMPLATE = (
    "Create {n} diverse personas for sharing perspectives on the topic: "
    '"{topic}".\n'
    "\n"
    "Return STRICT JSON:\n"
    "{{\n"
    '  "profiles": [\n'
    "    {{\n"
    '      "name": "string",\n'
    '      "age": int,\n'
    '      "personality": "single_word_trait",\n'
    '      "occupation": "short job title"\n'
    "    }}\n"
    "  ]\n"
    "}}\n"
    "\n"
    "Constraints:\n"
    "- Ages: 18-70, varied.\n"
    "- Personality: single word (letters/hyphens only), e.g., Analytical,\n"
    "  Pragmatic, Empathetic.\n"
    "- Occupation: concise job title or role (max 3 words).\n"
    "- Names: first name only; avoid duplicates.\n"
)


class AgentCoordinator:
    def __init__(
        self,
        model: str,
        client: AsyncOpenAI,
        topic: str,
        agent_count: int,
        display: LiveMultiPanelDisplay,
    ) -> None:
        self.client = client
        self.topic = topic
        self.agent_count = agent_count
        self.display = display
        self.model = model

    async def run_session(self) -> None:
        profiles = await self.generate_profiles()
        display_task = asyncio.create_task(self.display.run())
        tasks = []
        for i, p in enumerate(profiles):
            agent = Agent(
                agent_index=i,
                model=self.model,
                profile=p,
                client=self.client,
                display=self.display,
                topic=self.topic,
                agent_count=self.agent_count,
            )
            tasks.append(asyncio.create_task(agent.send_message()))

        await asyncio.gather(*tasks)
        await display_task

    async def generate_profiles(self) -> List[Dict]:
        print(
            f"\nGenerating {self.agent_count} user profile(s) to discuss "
            f"{self.topic}...\n"
        )
        resp = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": PROFILE_SYSTEM},
                {
                    "role": "user",
                    "content": PROFILE_USER_TEMPLATE.format(
                        n=self.agent_count,
                        topic=self.topic,
                    ),
                },
            ],
        )
        content = resp.choices[0].message.content or "{}"
        try:
            data = json.loads(content)
            profiles = data.get("profiles", [])
            clean_profiles = []
            names = set()
            for p in profiles:
                name = str(p.get("name", "")).strip()
                if not name or name in names:
                    continue
                names.add(name)
                age = int(p.get("age", 30))
                personality = str(p.get("personality", "")).strip()
                occupation = str(p.get("occupation", "")).strip()
                clean_profiles.append(
                    {
                        "name": name,
                        "age": age,
                        "personality": personality,
                        "occupation": occupation,
                    }
                )
            return clean_profiles[: self.agent_count]
        except Exception:
            return [
                {
                    "name": f"Agent {i+1}",
                    "age": 30 + i,
                    "occupation": "Unemployed",
                    "personality": "Calm",
                }
                for i in range(self.agent_count)
            ]
