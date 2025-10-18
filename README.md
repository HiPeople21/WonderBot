# WonderBot

An AI powered study guide creation app powered by the Perplexity API. 

WonderBot is a generative robot that can help users create a learning guide.
Nowadays, some people, especially students, find it difficult to learn systematically 
and informatively through the Internet. What Wonderbot aims to implement is 
generating a "learning guide" in PDF format that includes a step-by-step leading 
process, intended to help users start learning more quickly and easily.

We used the Perplexity API as a search and generation medium. The results are condensed
into a PDF, which contains all the questions and reading resources that a beginner needs.
All materials used are based from academic sources, providing high quality materials.
The icons and interface are user friendly.

WonderBot generated PDFs are available to everyone to view and download, as all generated PDFs
are accessible via the "List" page. This means that one may find previously generated resources,
which saves them time and effort. 

An easy form is displayed on the "Create" page, where the user enters a topic prompt, number of exercises,
and grade level. Perplexity is used to break the topic prompt into the main topic as well as many subtopics.

Team details:

- YuDong Zhao: Product assistant, database administrator [LinkedIn](https://www.linkedin.com/in/%E6%98%B1%E6%A0%8B-%E8%B5%B5-1ab35138a/)
- Yubo Wang: Frontend engineer, project manager [LinkedIn](https://www.linkedin.com/in/yubo-wang-b541302b3/)
- Stanley Hoo: Python backend developer [LinkedIn](https://www.linkedin.com/in/stanley-hoo-a20108331/)


Background video by: https://www.pexels.com/@joel-dunn-98388/

Loading animation from: https://tensor-svg-loaders.vercel.app/

Dimension by HTML5 UP
html5up.net | @ajlkn

# Installation & Setup

## 1) Prerequisites

* **Python** 3.10+
* **Pandoc**
* **LaTeX** engine with `xelatex` (TeX Live / MacTeX / MikTeX)

### macOS

```bash
brew install python pandoc
brew install --cask mactex
# If needed:
# echo 'export PATH="/Library/TeX/texbin:$PATH"' >> ~/.zshrc
```

### Ubuntu/Debian

```bash
sudo apt update
sudo apt install -y python3.11 python3.11-venv pandoc texlive-xetex texlive-latex-recommended texlive-latex-extra
# (Or: sudo apt install texlive-full  # large, but includes everything)
```

### Windows

* Install **Python** from [https://www.python.org](https://www.python.org)
* Install **Pandoc** (e.g., `winget install JohnMacFarlane.Pandoc`)
* Install **TeX Live** (`winget install TUG.TeXLive`) or **MikTeX**
* Ensure `xelatex` is on your PATH

---

## 2) Project Layout

```
your_project/
  app.py                 # Flask app (routes: /, /create, /list)
  search.py              # Content generation & PDF pipeline
  static/
    pdfs/                # PDF outputs written here
  templates/
    index.html           # Form page
  .env                   # API keys (created in step 4)
```

---

## 3) Virtual Environment & Dependencies

```bash
cd your_project
python -m venv .venv

# macOS/Linux
source .venv/bin/activate
# Windows (PowerShell)
# .venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## 4) Environment Variables

Create a file named `.env` in the project root:

```
PERPLEXITY_API_KEY=pk-xxxxxxxxxxxxxxxxxxxxxxxx
GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXX
```

> The Flask file references `PERPLEXITY_API_KEY`; ensure the name matches exactly.

---

## 5) Run the Flask App

```bash
# still in your venv
python app.py
```

Visit [http://localhost:5000](http://localhost:5000)

PDFs are generated inside `static/pdfs/`.

---

## 6) Troubleshooting

**A. Pandoc / LaTeX missing:**

* Error: `pandoc not found` → install Pandoc or `pypandoc-binary`
* Error: `xelatex not found` → install TeX Live or MikTeX and ensure PATH includes `xelatex`

**B. Missing LaTeX packages:**
Ensure the following are installed:

```tex
\usepackage{amsmath,amssymb,mathtools}
\usepackage{unicode-math}
\usepackage{physics}
\usepackage{siunitx}
```

**C. Create PDF output folder:**

```bash
mkdir -p static/pdfs
```

**D. Debug Pandoc build:**

```bash
pandoc test.md -o test.pdf --pdf-engine=xelatex
```

**E. Check API access:**
Ensure `.env` keys are valid and network allows outbound HTTPS.

---

## 7) Example Command Summary

```bash
# One-shot setup
python -m venv .venv && source .venv/bin/activate && \
  pip install flask requests python-dotenv perplexityai google-genai pypandoc && \
  mkdir -p static/pdfs && python app.py
```

---

✅ **After running**, visit: [http://localhost:5000](http://localhost:5000)
