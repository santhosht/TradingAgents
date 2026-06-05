# Analyse stocks with Claude (no API needed)

## One-time setup

```bash
cp .env.example .env
# Edit .env — set GOOGLE_API_KEY and uncomment the 3 Gemini lines
```

## Daily usage

```bash
source .venv/bin/activate
python fetch_data.py AMD        # replace AMD with any ticker
```

Then go to **claude.ai**, paste:
1. Contents of `AMD_data.txt`
2. Contents of `ANALYSIS_PROCESS.md`

Claude will ask which mode (Fast / Medium / Deep) and run the full analysis.
