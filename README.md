# ai-workspaces

A set of AI packages. Initially it includes a Deepseek API package.

Project structure using packages follows [uv workspace](https://docs.astral.sh/uv/concepts/projects/workspaces/) guidance.

## Curl example

```bash
curl -X POST http://localhost:8000/api/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"tell me a joke"}],"stream":true,"request_id":"test_123","model":"deepseek-reasoner"}'
```

Expected output

```text
data: {"type": "start"}

data: {"type": "start-step"}

data: {"type": "reasoning", "text": "Okay"}

data: {"type": "reasoning", "text": ", user just asked for a joke."}

data: {"type": "reasoning", "text": " Simple and straightforward request."}

data: {"type": "reasoning", "text": " They probably want a quick laugh or a mood booster."}

data: {"type": "reasoning", "text": " \n\n"}

data: {"type": "reasoning", "text": "Hmm, should I go classic or modern?"}

data: {"type": "reasoning", "text": " Since they didn't specify, I'll pick something universally relatable."}

data: {"type": "reasoning", "text": " Tech jokes usually work well - everyone deals with passwords."}

data: {"type": "reasoning", "text": " \n\n"}

data: {"type": "reasoning", "text": "*scrolling mental joke database* Ah!"}

data: {"type": "reasoning", "text": " The \"password\" pun."}

data: {"type": "reasoning", "text": " It's clean, self-deprecating tech humor, and the punchline sub"}

data: {"type": "reasoning", "text": "verts expectations twice: first with the obvious \"incorrect\" then"}

data: {"type": "reasoning", "text": " the meta twist about being a joke."}

data: {"type": "reasoning", "text": " \n\n"}

data: {"type": "reasoning", "text": "User might be: \n- On break needing distraction \n- Testing my humor function"}

data: {"type": "reasoning", "text": " \n- Genuinely wanting lighthearted content \n\n"}

data: {"type": "reasoning", "text": "Better keep delivery snappy."}

data: {"type": "reasoning", "text": " No setup explanation - the joke relies on surprise."}

data: {"type": "reasoning", "text": " Added asterisks for emphasis on the punchline."}

data: {"type": "reasoning", "text": " \n\n"}

data: {"type": "reasoning", "text": "..."}

data: {"type": "reasoning", "text": "wait, is \"incorrect\" too predictable?"}

data: {"type": "reasoning", "text": " Nah, the double fake-out saves it."}

data: {"type": "text", "text": "Sure!"}

data: {"type": "text", "text": " Here's a classic one for you:  \n\n"}

data: {"type": "text", "text": "**Why don't scientists trust atoms?"}

data: {"type": "text", "text": "**  \n*Because they make up everything!"}

data: {"type": "text", "text": "*  \n\n"}

data: {"type": "text", "text": "*(Bonus tech joke):*  \n**I told my computer I needed a"}

data: {"type": "text", "text": " break..."}

data: {"type": "text", "text": "**  \n*Now it won\u2019t stop sending me vacation ads.* \ud83d\ude04"}

data: {"type": "reasoning", "text": " *send*"}

data: {"type": "finish-step"}

data: {"type": "finish"}
```

## Prerequisites

- Python 3.13+ installed
- Docker & Docker Compose
- make (for convenience)

## Quick start (Docker Compose)

Simply clone the repo, add your Deepseek API key to the .env file and run make start:

```bash
cp ./packages/deepseek-api/.env_sample ./packages/deepseek-api/.env
```

```bash
make start
```

- API available at `http://localhost:8000`

## Linting & Formatting

The project uses [Ruff](https://docs.astral.sh/ruff/) for linting, formatting and sorting imports for code consistency. Simply run:

```bash
make format
```
