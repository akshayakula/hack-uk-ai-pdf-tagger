# hack-uk-ai-pdf-tagger

## Current Limitations

Works for documents that have been initially, however incompletely, tagged.

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

### Environment Config

Add a .dotenv-file with a `MISTRAL_API_KEY=` entry to the repo directory.

### Run Command

```
poetry run streamlit run pdfstral.py
```

## Resources

PDF:

* https://opensource.adobe.com/dc-acrobat-sdk-docs/library/overview/Overview_Metadata.html

Tools:

* https://pymupdf.readthedocs.io/en/latest/pymupdf4llm/index.html
* https://pikepdf.readthedocs.io/en/latest/topics/metadata.html