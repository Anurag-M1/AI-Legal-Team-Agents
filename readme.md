# AI Legal Team Agents

AI-powered legal analysis system built with multiple specialized agents for:
- contract review
- legal research
- risk assessment
- compliance checks

Upload a legal PDF, process it into a knowledge base, and get a structured legal report with key points and recommendations.

<img width="1446" height="791" alt="ALTA" src="https://github.com/user-attachments/assets/850e526d-e219-4dee-9a2d-095fbe84f571" />

## Features

- Multi-agent workflow:
  - `LegalAdvisor` for legal research and citations
  - `ContractAnalyst` for clause and obligation analysis
  - `LegalStrategist` for risks and strategy
  - `Team Lead` for final integrated report
- PDF ingestion with chunking and vector search
- OpenRouter model support using `qwen/qwen3-coder`
- Streamlit UI for end-to-end analysis

## Tech Stack

- Python
- Streamlit
- Agno
- LanceDB
- DuckDuckGo Search
- OpenRouter

## Project Structure

```text
.
├── legal_team.py        # Main Streamlit app
├── requirements.txt
└── sample_contract.pdf
```

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/anurag-m1/AI-Legal-Team-Agents.git
cd AI-Legal-Team-Agents
```

### 2. Create and activate virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
streamlit run legal_team.py
```

## Usage

1. Open the Streamlit app in your browser.
2. Enter your OpenRouter API key in the sidebar.
3. Upload a legal PDF.
4. Select analysis type:
   - Contract Review
   - Legal Research
   - Risk Assessment
   - Compliance Check
   - Custom Query
5. Click `Analyze` to generate results.

## Configuration

The app expects an OpenRouter key. You can set it in the UI, or via environment variables:

```bash
export OPENROUTER_API_KEY="your_key_here"
export OPENAI_API_KEY="your_key_here"
```

## Troubleshooting

- `502 Failed to authenticate request with Clerk`:
  - Re-paste your OpenRouter API key (ensure no extra spaces).
  - Verify key is active and account has available credits.
  - Retry after a short wait (can be a temporary provider-side issue).

## Disclaimer

This project provides AI-assisted legal analysis for educational and productivity purposes. It is not legal advice.

## Author

**Anurag Kumar Singh**

- GitHub: [github.com/anurag-m1](https://github.com/anurag-m1)
- Instagram: [instagram.com/ca_anuragsingh](https://instagram.com/ca_anuragsingh)
