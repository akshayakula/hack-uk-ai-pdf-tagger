# hack-uk-ai-pdf-tagger

## Setup Notes

### Windows

One setup option is to use venv, the Python package manager, for Python version control if the system installation does not match the required version (see `.python-version`). To get python:

```
./python-3.12.exe /quiet InstallAllUsers=1 TargetDir=C:\Python312 PrependPath=1
```

One setup option is to use venv, the Python package manager, for Python version control if the system installation does not match the required version (see `.python-version`): 

```
py -3.12 -m venv .venv
.venv\Scripts\activate
```

Once you have this right, and installed poetry into the active environment with `python -m pip install poetry` the setup requires the following run command(s).

### Package Management

```
poetry install
```

### Run Command

```
poetry run streamlit run pdfstral.py
```