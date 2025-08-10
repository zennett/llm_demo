import json
from pathlib import Path
from typing import Any, Dict

CACHE_DIR = Path(".cache")
CACHE_DIR.mkdir(exist_ok=True)


def responses_path(topic: str) -> Path:
    topic_filename = topic.strip().lower().replace("/", "_").replace(" ", "_")
    return CACHE_DIR / f"{topic_filename}.json"


def save_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(exist_ok=True, parents=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def init_topic(topic: str) -> Dict[str, Any]:
    response_path = responses_path(topic)
    state = {
        "topic": topic,
        "messages": [],
    }
    save_json(response_path, state)
    return state


def load_topic(topic: str) -> Dict[str, Any]:
    response_path = responses_path(topic)
    data = load_json(response_path)
    if not data:
        data = init_topic(topic)
    return data


def append_message(
    topic: str,
    name: str,
    age: int,
    occupation: str,
    personality: str,
    response: str,
) -> None:
    data = load_topic(topic)
    data.setdefault("messages", []).append(
        {
            "name": name,
            "age": age,
            "occupation": occupation,
            "personality": personality,
            "response": response,
        }
    )
    save_json(responses_path(topic), data)
