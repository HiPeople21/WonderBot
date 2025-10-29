# WonderBot: AI-Powered Study Guide Generator

WonderBot is an AI-powered application that helps students learn faster and more effectively using the Perplexity API.

Imagine you’re a college student with a final exam in quantum physics in just three hours. Normally, you’d have to skim through dense textbook chapters, decode complicated jargon, and then spend more time searching for relevant practice problems online—most of which aren’t even useful.

WonderBot solves all of that. Simply tell it what you want to learn. For example:

```“I want to learn about particle wave duality, quantum entanglement, superconductors, and the measurement problem.”```

The app automatically breaks your prompt into a main topic and subtopics, searches academic sources (MIT, Harvard, Caltech, etc.), and compiles everything into a concise, easy-to-read PDF. Each packet includes textbook-style explanations, key formulas, worked examples, and high-quality practice problems with solutions.

But WonderBot isn’t just for college students—anyone can use it. The material automatically adapts to your education level. For example, if you select “elementary school,” the app will pull sources from kid-friendly sites like Khan Academy and other educational organizations.

Beyond individual learning, **WonderBot is built around community-driven education**. All generated PDFs are stored on your personal My Lists page, where users can revisit or download their past study guides. You can also publish your PDFs to the shared WonderBot library, allowing other learners to explore, download, and build upon the guides you’ve created.

By sharing resources, students and enthusiastic learners around the world can collaborate, discover new topics, and contribute to an ever-growing network of high-quality study materials. With its intuitive interface and AI-powered learning engine, WonderBot turns studying into a collective experience—making education faster, clearer, and more connected.

Live site can be viewed [here](https://wonderbot.stanleyhoo1.tech/).

---

### **An example learning packet using the above prompt, 8 questions, and university level parameters can be viewed here: [Quantum Physics Packet](https://github.com/HiPeople21/WonderBot/blob/main/example.pdf)**

---

Team details:

- YuDong Zhao: Product assistant [LinkedIn](https://www.linkedin.com/in/%E6%98%B1%E6%A0%8B-%E8%B5%B5-1ab35138a/)
- Yubo Wang: Frontend engineer, project manager [LinkedIn](https://www.linkedin.com/in/yubo-wang-b541302b3/)
- Stanley Hoo: Backend lead, API calls, database management [LinkedIn](https://www.linkedin.com/in/stanley-hoo/)

Background video by: https://www.pexels.com/@joel-dunn-98388/

Loading animation from: https://tensor-svg-loaders.vercel.app/

Dimension by HTML5 UP
html5up.net | @ajlkn

# Installation & Setup

## 1) Prerequisites

* **Python** 3.10+
* Perplexity API Key
* Gemeni API Key
* Secret Key (optional)

### Ubuntu/Debian/WSL

```bash
sudo apt update
sudo apt install texlive-full
sudo apt install pandoc
```

---

## 2) Project Layout

```
WonderBot/
  requirements.txt
  venv/
  src/
    main.py                # Flask app 
    search.py              # Content generation & PDF pipeline
    static/
      pdfs/                # PDF outputs written here
    templates/
      index.html           # Form page
    .env                   # API keys (created in step 4) and secret key
  README.md
  LICENSE.txt
  .gitignore
```

---

## 3) Virtual Environment & Dependencies

```bash
cd WonderBot (or whatever you named this folder)
python3 -m venv venv

# macOS/Linux
source venv/bin/activate

# Windows (PowerShell)
venv\Scripts\Activate.ps1

python3 -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## 4) Environment Variables

Create a file named `.env` in the src folder:

```
PERPLEXITY_API_KEY=pk-xxxxxxxxxxxxxxxxxxxxxxxx
GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXX
SECRET_KEY=wr-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

> The Flask file references `PERPLEXITY_API_KEY`, `GEMENI_API_KEY`, and `SECRET_KEY`; ensure the name matches exactly.

---

## 5) Run the Flask App

```bash
python3 main.py
```

Visit [http://localhost:5000](http://localhost:5000)

PDFs are generated inside `static/pdfs/` or can be viewed on the website.

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

✅ **After running**, visit: [http://localhost:5000](http://localhost:5000)
