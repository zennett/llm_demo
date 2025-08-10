# Multi-Agent Persona Discussion CLI

A Python command-line tool that generates diverse AI personas and streams their thoughts on a given topic in real time to distinctly colored terminal panels.

## Overview
- **Automatic persona creation** - Generates realistic, varied profiles (name, age, occupation, personality).
- **Multiple agents** - Run 1–7 agents simultaneously.
- **Live streaming UI** - Rich terminal display updates as each agent responds token-by-token.
- **Configurable model** - Works with any OpenAI chat model (default: `gpt-4o-mini`).
- **Local caching** - Saves conversations for later review in `.cache/`.

## Feature Highlights
- **Asynchronous I/O** - Agents stream responses in parallel without blocking calls.
- **Structured prompt generation** - Uses deterministic templates for persona creation and responses.
- **Live concurrent rendering** - Streams partial tokens from multiple sources to the terminal.
- **Extensible design** - Modular components (`Agent`, `AgentCoordinator`, `LiveMultiPanelDisplay`) allow for easy integration with other frontends or storage layers.
- **Persistence layer** - Writes structured JSON conversation logs for replay, analytics, or testing.

## Installation
```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY="OPENAI_API_KEY"
python -m llm_demo.cli --topic "Artificial intelligence in marketing" --agents 7