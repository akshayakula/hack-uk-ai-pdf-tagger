# hack-uk-ai-pdf-tagger: ["PDFstal"](https://pdfstral.streamlit.app/) <img src="./mistral_logo.png" alt="Mistral Logo" width="100"/>

## 🌟 Intro: A [Mistral AI <> a16z London Hackathon](https://cerebralvalley.notion.site/Mistral-AI-a16z-London-Hackathon-Event-Details-Hackers-62cdf3e742a745aa9f4c31d20a8882af) Project

Please see [these slides](https://docs.google.com/presentation/d/18mkzttmRAo7kTcdBRxyERATSdmqt9ODidUBlRLN30Mg/edit?usp=sharing) for what this project is about.

## 🚧 Current Limitations & Vision

⚠️ Works for documents that have been initially, however incompletely, tagged - this is due to the Python libraries for PDFs used. Java- or .NET-based frameworks like iText and PDFBox might be stops in the future.  
🎯 We demonstrate nice add-on functionality like speech synthesis here, but the core idea was really **PDF-provisioning-assistance** (helping in the annotation process, not in the reading) because of an infrastructure-first, accessibility-driven vision of democratic document repositories.

## ⚙️ Setup Notes

### 💻 Windows

One setup option is to use venv, the Python package manager, for Python version control if the system installation does not match the required version (see `.python-version`). To get Python:

```
./python-3.12.exe /quiet InstallAllUsers=1 TargetDir=C:\Python312 PrependPath=1
```

One setup option is to use venv, the Python package manager, for Python version control if the system installation does not match the required version (see `.python-version`): 

```
py -3.12 -m venv .venv
.venv\Scripts\activate
```

Once you have this right, and installed poetry into the active environment with `python -m pip install poetry` the setup requires the following run command(s).

### 📦 Package Management

```
poetry install
```

### 🌍 Environment Config

Add a .dotenv-file with a `MISTRAL_API_KEY=` entry to the repo directory.

### ▶️ Run Command

```
poetry run streamlit run pdfstral.py
```

## 📚 Resources

📄 PDF Resources:

* https://opensource.adobe.com/dc-acrobat-sdk-docs/library/overview/Overview_Metadata.html

🛠️ Tools:

* https://pymupdf.readthedocs.io/en/latest/pymupdf4llm/index.html
* https://pikepdf.readthedocs.io/en/latest/topics/metadata.html