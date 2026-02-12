# AI Legal Team Agents

AI Legal Team Agents provides legal document analysis with a multi-agent workflow (research, contract analysis, strategy, and synthesis).

This repo now supports:
- Vercel deployment via serverless Python API (`/api/index.py`)
- Local Streamlit UI (`legal_team.py`)

<img width="1446" height="791" alt="ALTA" src="https://github.com/user-attachments/assets/850e526d-e219-4dee-9a2d-095fbe84f571" />

## Vercel Deployment

### 1. Push repo to GitHub

Already connected repo:
- [github.com/Anurag-M1/AI-Legal-Team-Agents](https://github.com/Anurag-M1/AI-Legal-Team-Agents)

### 2. Import project in Vercel

1. Open [vercel.com/new](https://vercel.com/new)
2. Import this GitHub repository
3. Keep default project settings

### 3. Add environment variables in Vercel

Add in Project Settings -> Environment Variables:

- `OPENROUTER_API_KEY` = your OpenRouter key
- `OPENROUTER_MODEL_ID` = `qwen/qwen3-coder` (optional, default already set)
- `MAX_DOC_CHARS` = `45000` (optional)

### 4. Deploy

Trigger deployment from Vercel UI or CLI:

```bash
vercel --prod
```

## API Endpoints (Vercel)

- `GET /api` : service info
- `GET /api/health` : health check
- `POST /api/analyze` : upload PDF + run legal analysis
- `POST /api/analyze-text` : analyze plain text payload

### Example: analyze PDF

```bash
curl -X POST "https://your-project.vercel.app/api/analyze" \
  -F "file=@sample_contract.pdf" \
  -F "analysis_type=Contract Review"
```

### Example: analyze text

```bash
curl -X POST "https://your-project.vercel.app/api/analyze-text" \
  -H "Content-Type: application/json" \
  -d '{
    "analysis_type": "Risk Assessment",
    "query": "Identify high-risk clauses",
    "text": "Contract text goes here"
  }'
```

## Local Streamlit (Optional)

Use local UI if you want the Streamlit experience.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-streamlit.txt
export OPENROUTER_API_KEY="your_key_here"
streamlit run legal_team.py
```

## Project Structure

```text
.
├── api/
│   └── index.py
├── legal_team.py
├── vercel.json
├── requirements.txt
└── requirements-streamlit.txt
```

## Troubleshooting

- `502 Failed to authenticate request with Clerk`
  - Verify `OPENROUTER_API_KEY` is valid and active
  - Check OpenRouter credits/billing
  - Retry after a short wait

## Disclaimer

This project provides AI-assisted legal analysis for education and productivity purposes. It is not legal advice.

## Author

**Anurag Kumar Singh**

- GitHub: [github.com/anurag-m1](https://github.com/anurag-m1)
- Instagram: [instagram.com/ca_anuragsingh](https://instagram.com/ca_anuragsingh)
