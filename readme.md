# AI Legal Team Agents

AI-powered legal analysis app for:
- contract review
- legal research
- risk assessment
- compliance checks

It uses a multi-agent workflow (`LegalAdvisor`, `ContractAnalyst`, `LegalStrategist`, `Team Lead`) with OpenRouter (`qwen/qwen3-coder`).

<img width="1446" height="791" alt="ALTA" src="https://github.com/user-attachments/assets/850e526d-e219-4dee-9a2d-095fbe84f571" />

## Deploy on Render

This repo includes `render.yaml` for one-click Blueprint deploy.

### Option A: Blueprint Deploy (recommended)

1. Push this repo to GitHub.
2. In Render, go to **New +** -> **Blueprint**.
3. Select this repository.
4. Set required environment variable:
   - `OPENROUTER_API_KEY`
5. Deploy.

### Option B: Manual Web Service

1. In Render, create **New Web Service** from this repo.
2. Use:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run legal_team.py --server.port $PORT --server.address 0.0.0.0`
3. Add env var:
   - `OPENROUTER_API_KEY`
4. Deploy.

## Local Run

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export OPENROUTER_API_KEY="your_key_here"
streamlit run legal_team.py
```

## Project Structure

```text
.
├── legal_team.py
├── requirements.txt
└── render.yaml
```

## Notes

- Do not hardcode API keys in source code.
- If you see `502 Failed to authenticate request with Clerk`, verify OpenRouter key + credits.

## Author

**Anurag Kumar Singh**

- GitHub: [github.com/anurag-m1](https://github.com/anurag-m1)
- Instagram: [instagram.com/ca_anuragsingh](https://instagram.com/ca_anuragsingh)
