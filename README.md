# hack-uk-ai-pdf-tagger

## Setup Notes

### Windows

One setup option is to use venv, the Python package manager, for Python version control if the system installation does not match the required version (see `.python-version`): once you have this right, and installed poetry into the active environment with `python -m pip install poetry` the setup requires the following run command(s).

### Run Command

```
poetry run streamlit run pdfstral.py
```