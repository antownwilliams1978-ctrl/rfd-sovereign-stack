# rfd-sovereign-stack

A sovereign, portable, and cost-effective e-commerce platform for the Red Feather Dynasty, built on a Vultr-ready headless architecture. · Built with Manus.

## SEBEK package-native layout

- Primary package: `sebek/`
  - Dashboard: `sebek/dashboard.py`
  - Ingestion CLI: `sebek/ingestion_cli.py`
  - Speech agent: `sebek/speech/agent.py`
- Root-level `sebek_dash.py`, `sebek_speech_agent.py`, and `sebek_mass_digest.py` are compatibility wrappers (deprecated).

## Run SEBEK locally

```bash
pip install -e .
```

### Dashboard (Streamlit)

```bash
streamlit run sebek/dashboard.py
```

The dashboard now includes a **Speech Agent** tab that starts/stops the package-native
`python -m sebek.speech.agent` process and shows persisted runtime status.

### Speech agent

```bash
python -m sebek.speech.agent
```

If you use the dashboard controls, let the dashboard manage the speech agent instead of
starting a second copy manually or through systemd at the same time.

### Ingestion

```bash
python -m sebek.ingestion_cli
```
