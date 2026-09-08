# rfd-sovereign-stack

A sovereign, portable, and cost-effective e-commerce platform for the Red Feather Dynasty, built on a Vultr-ready headless architecture. · Built with Manus.

## SEBEK package-native layout

- Primary package: `sebek/`
  - Dashboard: `sebek/dashboard.py`
  - Ingestion CLI: `sebek/ingestion_cli.py`
  - Speech agent: `sebek/speech/agent.py`
- Root-level `sebek_dash.py` and `sebek_speech_agent.py` are compatibility wrappers (deprecated).

## Run SEBEK locally

```bash
pip install -e .
```

### Dashboard (Streamlit)

```bash
streamlit run sebek/dashboard.py
```

### Speech agent

```bash
python -m sebek.speech.agent
```

### Ingestion

```bash
python -m sebek.ingestion_cli
```
