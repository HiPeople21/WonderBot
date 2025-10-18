import os
import json
import requests
from hashlib import sha256
import pathlib
from dotenv import load_dotenv
from datetime import datetime
import re
import pypandoc
from google import genai

load_dotenv()

BASE_PATH = pathlib.Path(__file__).parent

PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def assert_api_key():
    if not PERPLEXITY_API_KEY or PERPLEXITY_API_KEY.strip() == "":
        raise RuntimeError("PERPLEXITY_API_KEY is missing or empty")


########################################################################################
# ----------------- Generates Textbook-style Lessons -----------------
########################################################################################


# Temperature 0.2 for focused, less random output
def create_lesson(messages, *, temperature=0.2, max_tokens=8000, debug=True):
    assert_api_key()
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "content-type": "application/json",
    }
    payload = {
        "model": "sonar-pro",
        "messages": messages,
        "temperature": temperature,
        "top_p": 0.9,
        "max_tokens": max_tokens,  # raise cap to reduce truncation
        "stream": False,
        "enable_search_classifier": True,
        "return_search_results": False,
    }
    try:
        r = requests.post(PERPLEXITY_API_URL, json=payload, headers=headers, timeout=90)
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"HTTP request failed: {e}")

    if debug:
        print(f"[perplexity] status={r.status_code}")
        # print only first 800 chars to avoid flooding logs
        print(f"[perplexity] body head: {r.text[:800]}")

    # Explicitly raise HTTP errors
    try:
        r.raise_for_status()
    except requests.HTTPError as he:
        raise RuntimeError(f"API error {r.status_code}: {r.text}") from he

    data = r.json()
    # Defensive: ensure choices exist
    if not isinstance(data, dict) or "choices" not in data or not data["choices"]:
        raise RuntimeError(f"Unexpected response structure: {json.dumps(data)[:800]}")
    content = data["choices"][0].get("message", {}).get("content", "")
    if not content:
        raise RuntimeError(f"No content returned: {json.dumps(data)[:800]}")
    return content


SCHEMA_HINT = {
    "type": "object",
    "required": [
        "title",
        "learning_path",
        "sections",
        "summary",
        "estimated_total_read_time_minutes",
        "citations",
    ],
    "properties": {
        "title": {"type": "string"},
        "learning_path": {"type": "array", "items": {"type": "string"}},
        "sections": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "title",
                    "overview",
                    "key_points",
                    "formulas",
                    "diagram",
                    "worked_example",
                    "common_pitfalls",
                    "mini_quiz",
                ],
                "properties": {
                    "title": {"type": "string"},
                    "overview": {"type": "string"},
                    "key_points": {"type": "array", "items": {"type": "string"}},
                    "formulas": {"type": "array", "items": {"type": "string"}},
                    "derivations": {"type": "string"},
                    "diagram": {
                        "type": "object",
                        "required": ["caption", "instructions"],
                        "properties": {
                            "caption": {"type": "string"},
                            "instructions": {"type": "string"},
                        },
                    },
                    "worked_example": {
                        "type": "object",
                        "required": ["prompt", "steps", "answer"],
                        "properties": {
                            "prompt": {"type": "string"},
                            "steps": {"type": "array", "items": {"type": "string"}},
                            "answer": {"type": "string"},
                        },
                    },
                    "common_pitfalls": {"type": "array", "items": {"type": "string"}},
                    "mini_quiz": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["q", "a"],
                            "properties": {
                                "q": {"type": "string"},
                                "a": {"type": "string"},
                            },
                        },
                    },
                },
            },
        },
        "summary": {"type": "string"},
        "estimated_total_read_time_minutes": {"type": "integer"},
        "citations": {"type": "array", "items": {"type": "string"}},
    },
}

SYSTEM_MSG = (
    "You are a master educator. Write like a concise textbook: clean, precise, structured. "
    "Short paragraphs (plain text), minimal jargon, clear notation. "
    "No links or markdown in ALL fields. Citations ONLY go in the 'citations' field. The citation should ONLY include the link to the source. Return ONLY valid JSON. "
)


def find_textbook_packet(
    topic: str,
    subtopics: list[str],
    grade_level: str,
    max_sections: int = 6,
    quiz_per_section: int = 3,
    debug=True,
) -> dict:
    subtopics_txt = ", ".join(subtopics) if subtopics else "—"
    user_msg = f"""
Create a condensed, concise textbook-style packet for a {grade_level} student.

Primary topic: "{topic}"
Focus subtopics (include and integrate): {subtopics_txt}

Constraints and style:
- Clarity and density. Short paragraphs (plain text), precise definitions, minimal fluff.
- Logical learning order (prerequisites first).
- Each section: 120-400 word overview, 3-6 key points, essential formulas (LaTeX ok),
  1 worked example with steps, 1 small diagram described by text (caption + drawing instructions),
  2-4 common pitfalls, and {quiz_per_section} mini-quiz Q/A.
- Keep derivations brief (5-10 lines) only when essential.
- DO NOT include citations, URLs, references, or markdown.
- Keep total number of sections ≤ {max_sections} by merging closely related subtopics.

Output:
Return ONLY valid JSON matching this schema (no prose outside JSON):
{json.dumps(SCHEMA_HINT)}
""".strip()

    #### EDIT ABOVE TO INCLUDE IMAGES

    content = create_lesson(
        [
            {"role": "system", "content": SYSTEM_MSG},
            {"role": "user", "content": user_msg},
        ],
        max_tokens=8000,
        debug=debug,
    )
    parsed = json_sanitize(content)
    if not parsed:
        # fail-soft: small skeleton so downstream doesn’t crash
        return {
            "title": f"{topic} — Learning Packet",
            "learning_path": subtopics or [topic],
            "sections": [
                {
                    "title": "Overview",
                    "overview": "Content unavailable due to JSON parse or token limit.",
                    "key_points": [],
                    "formulas": [],
                    "derivations": "",
                    "diagram": {"caption": "—", "instructions": "—"},
                    "worked_example": {"prompt": "—", "steps": [], "answer": "—"},
                    "common_pitfalls": [],
                    "mini_quiz": [],
                }
            ],
            "summary": "Generation failed softly; check API logs.",
            "estimated_total_read_time_minutes": 3,
        }
    return parsed


########################################################################################
# ----------------- Generates Practice Problems via Web Search -----------------
########################################################################################

OPENLY_LICENSED_HINT = """
Prefer openly licensed or university sources where verbatim copying is permitted:
- ocw.mit.edu, web.mit.edu (MIT OCW)
- openstax.org
- physics.mit.edu, physics.ucsb.edu, physics.berkeley.edu
- stanford.edu, harvard.edu, berkeley.edu, cmu.edu, utexas.edu, ucsd.edu, illinois.edu
- arizona.edu, colorado.edu, umich.edu, cornell.edu
- Any *.edu domain with problem sets or PDF solutions
- khanacademy.org
- archive.org (for archived textbooks with open licenses)
Avoid: paywalled sites, copyrighted textbooks without open licenses, commercial worksheets.
"""


def build_messages(topic, subtopics, grade_level, num_problems):
    subtopics_txt = ", ".join(subtopics) if subtopics else "—"
    today = datetime.today().strftime("%Y-%m-%d")

    system = (
        "You are a meticulous web research assistant that returns ONLY verbatim practice problems "
        "and their official solutions from credible, preferably open-licensed sources. "
        "You must search the live web. Never paraphrase or invent content. Always cite the exact URL."
    )

    # Strict JSON schema & counting rules
    schema = {
        "type": "array",
        "minItems": num_problems,
        "maxItems": num_problems,
        "items": {
            "type": "object",
            "required": [
                "question",
                "solution",
                "source_title",
                "source_url",
                "license",
            ],
            "properties": {
                "question": {"type": "string"},  # verbatim
                "solution": {"type": "string"},  # verbatim
                "source_title": {"type": "string"},
                "source_url": {"type": "string"},
                "license": {
                    "type": "string"
                },  # e.g., "MIT OCW CC BY-NC-SA", "University PDF (educational use)"
            },
        },
    }

    user = f"""
Goal:
Find exactly {num_problems} (no more, no less) high-quality practice problems for:
- Topic: {topic}
- Subtopics: {subtopics_txt}
- Grade level: {grade_level}
- Date context: {today}

Requirements (critical):
1) Search the web and pick problems from credible sources, ideally open-license. {OPENLY_LICENSED_HINT}
2) Return the problem **question** and the **official solution** **verbatim** (copy text exactly; do NOT paraphrase or summarize).
3) Include the **source_title**, **source_url**, and **license**/rights note if present on the page (e.g., 'CC BY-NC-SA').
4) If a single page has multiple suitable problems, you may select more than one from that page.
5) Exclude duplicates and trivial problems.
6) If insufficient items are found on preferred domains, broaden to other .edu domains or archived PDFs until you reach exactly {num_problems}.
7) Output **ONLY valid JSON** matching this schema (no prose, no markdown): {json.dumps(schema)}
8) Try to give at least one problem per subtopic if possible.
9) Prioritize problems with complete solutions (work shown, final answer).
10) Prioritize problems with multiple parts (a, b, c...) for depth.

Important format rules:
- Preserve original line breaks and math formatting (use plaintext; you may include ASCII math like 'F = ma').
- Do NOT include any commentary, headings, or extra keys.
- The array MUST contain exactly {num_problems} items.
"""

    # Optional domain-bias hint inside the last user message improves retrieval quality
    domain_bias = (
        "Search hints (you may vary as needed): "
        "site:ocw.mit.edu OR site:web.mit.edu OR site:openstax.org OR site:*.edu filetype:pdf "
        f'"{topic}" {" ".join(subtopics or [])} practice problems solutions'
    )

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user + "\n\n" + domain_bias},
    ]


def _strict_json_load(maybe_json: str):
    """Best-effort to recover a JSON array if the model wraps it in stray text."""
    try:
        return json.loads(maybe_json)
    except json.JSONDecodeError:
        start, end = maybe_json.find("["), maybe_json.rfind("]")
        if start != -1 and end != -1:
            return json.loads(maybe_json[start : end + 1])
        raise


def _validate_items(items, num_expected):
    if not isinstance(items, list) or len(items) != num_expected:
        raise ValueError(
            f"Expected exactly {num_expected} items, got {len(items) if isinstance(items, list) else 'non-list'}"
        )
    url_re = re.compile(r"^https?://", re.I)
    for i, it in enumerate(items, 1):
        for k in ["question", "solution", "source_title", "source_url", "license"]:
            if k not in it or not isinstance(it[k], str) or not it[k].strip():
                raise ValueError(f"Item {i} missing/empty field: {k}")
        if not url_re.match(it["source_url"]):
            raise ValueError(f"Item {i} has invalid source_url: {it['source_url']}")
        # Basic verbatim sanity: avoid obvious paraphrase markers
        if (
            "paraphrase" in it["question"].lower()
            or "paraphrase" in it["solution"].lower()
        ):
            raise ValueError(f"Item {i} looks paraphrased.")
    return True


def create_practice_problems(
    topic,
    subtopics,
    grade_level,
    num_problems,
    max_tokens=8000,
    temperature=0.2,
    debug=True,
):
    """
    Uses Perplexity Sonar to fetch EXACTLY `num_problems` practice problems with verbatim questions & solutions
    from credible/open sources (preferring MIT OCW, OpenStax, and .edu problem sets).
    Returns a Python list of dicts: [{question, solution, source_title, source_url, license}, ...]
    """
    assert_api_key()

    messages = build_messages(topic, subtopics, grade_level, num_problems)

    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "content-type": "application/json",
    }
    payload = {
        "model": "sonar-pro",
        "messages": messages,
        "temperature": temperature,
        "top_p": 0.9,
        "max_tokens": max_tokens,
        "stream": False,
        "enable_search_classifier": True,
        "return_search_results": True,
    }

    try:
        r = requests.post(PERPLEXITY_API_URL, json=payload, headers=headers, timeout=90)
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"HTTP request failed: {e}")

    if debug:
        print(f"[perplexity] status={r.status_code}")
        print(f"[perplexity] body head: {r.text[:800]}")

    try:
        r.raise_for_status()
    except requests.HTTPError as he:
        raise RuntimeError(f"API error {r.status_code}: {r.text}") from he

    data = r.json()
    if not isinstance(data, dict) or "choices" not in data or not data["choices"]:
        raise RuntimeError(f"Unexpected response structure: {json.dumps(data)[:800]}")

    content = data["choices"][0].get("message", {}).get("content", "")
    if not content:
        raise RuntimeError(f"No content returned: {json.dumps(data)[:800]}")

    # Parse + validate strict JSON
    items = _strict_json_load(content)
    _validate_items(items, num_problems)
    return items


##########################################################################################
# ------------------------------------ Formatting ----------------------------------------
##########################################################################################


def json_sanitize(s: str):
    try:
        return json.loads(s)
    except Exception:
        for a, b in [("{", "}"), ("[", "]")]:
            i, j = s.find(a), s.rfind(b)
            if i != -1 and j != -1 and j > i:
                try:
                    return json.loads(s[i : j + 1])
                except Exception:
                    pass
    return None


def textbook_json_to_markdown(packet: dict) -> str:
    md = [f"# {packet.get('title', 'Learning Packet')}\n"]
    md.append(
        f"**Estimated reading time:** {packet.get('estimated_total_read_time_minutes', '~')} minutes\n"
    )
    lp = packet.get("learning_path") or []
    if lp:
        md.append("**Learning order:** " + " → ".join(lp) + "\n")
    for section in packet.get("sections", []):
        md.append(f"## {section.get('title', 'Section')}\n")
        if section.get("overview"):
            md.append(section["overview"] + "\n")
        if section.get("key_points"):
            md.append("**Key points:**")
            for p in section["key_points"]:
                md.append(f"- {p}")
        if section.get("formulas"):
            md.append("**Formulas:**")
            for f in section["formulas"]:
                md.append(f"- `{f}`")
        if section.get("derivations"):
            md.append("**Sketch derivation:**")
            md.append(section["derivations"])
        if section.get("worked_example"):
            ex = section["worked_example"]
            md.append("\n**Worked Example:**")
            if ex.get("prompt"):
                md.append(f"*{ex['prompt']}*")
            for step in ex.get("steps", []):
                md.append(f"  - {step}")
            if ex.get("answer"):
                md.append(f"**Answer:** {ex['answer']}\n")
        if section.get("diagram"):
            d = section["diagram"]
            md.append("**Diagram:** " + d.get("caption", ""))
            if d.get("instructions"):
                md.append("Instructions: " + d["instructions"])
        if section.get("common_pitfalls"):
            md.append("**Common Pitfalls:**")
            for p in section["common_pitfalls"]:
                md.append(f"- {p}")
        if section.get("mini_quiz"):
            md.append("**Quick Quiz:**")
            for qa in section["mini_quiz"]:
                md.append(f"- {qa.get('q', '')}  \n  **Ans:** {qa.get('a', '')}")
        md.append("\n\n")
    if packet.get("summary"):
        md.append("## Summary\n" + packet["summary"])
    return "\n".join(md)


def fix_markdown(markdown: str) -> str:
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "content-type": "application/json",
    }
    payload = {
        "model": "sonar-pro",
        "messages": [
            {
                "role": "system",
                "content": (
                    "Reformat the user text into valid, consistent Markdown. "
                    "Headings must be proper Markdown headings (lines starting with 1-6 '#' followed by a space). "
                    "Use `$...$` for inline math and `$$...$$` for display math. "
                    "Do NOT use \\(...\\) or \\[...\\]. "
                    "Do not invent content, only fix delimiters and close all formatting markers. "
                    "Make sure all backticks, asterisks, and dollar signs are balanced."
                ),
            },
            {
                "role": "user",
                "content": f"Rewrite this as valid Markdown with balanced math delimiters and headers. Only return the Markdown:\n\n{markdown}",
            },
        ],
        "max_tokens": 20000,
        "temperature": 0.2,
        # "stream": True,
        # "web_search_options": {"search_type": "pro"},
    }

    r = requests.post(PERPLEXITY_API_URL, headers=headers, json=payload, timeout=90)
    r.raise_for_status()
    content = r.json()["choices"][0]["message"]["content"].strip()

    # If model wrapped in fences, strip them safely
    if content.startswith("```"):
        first_nl = content.find("\n")
        last_ticks = content.rfind("```")
        if first_nl != -1 and last_ticks != -1 and last_ticks > first_nl:
            content = content[first_nl + 1 : last_ticks].strip()

    return content


# Fix numbering
NUM_PREFIX_RE = re.compile(
    r"""^\s*(
        (?:problem\s*)?\d+[\).\:]    |  # "Problem 3:" / "3." / "3)"
        (?:Q(?:uestion)?\s*)?\d+[\).\:] |
        [\(\[]?\d+[\)\]]\s*           |  # "(3)" "[3]"
        [IVXLCM]+[\).\:]              |  # roman numerals
        [a-zA-Z][\).\:]\s*               # "a)" "b."
    )\s*""",
    re.IGNORECASE | re.VERBOSE,
)


def strip_leading_numbering(text: str) -> str:
    # remove numbering only from the first line, keep subparts inside
    lines = text.lstrip().splitlines()
    if lines:
        lines[0] = NUM_PREFIX_RE.sub("", lines[0]).lstrip()
    return "\n".join(lines).rstrip()


MATH_CMDS = r"(vec|frac|cdot|times|ldots|nabla|partial|sqrt|sum|prod|int|lim|log|ln|sin|cos|tan|alpha|beta|gamma|Delta|leq|geq|pm)"


def sanitize_markdown_for_latex(md: str) -> str:
    """
    Preflight sanitizer to reduce LaTeX build errors from Pandoc.
    - Normalizes math delimiters to $...$ (inline) and $$...$$ (display)
    - Ensures math commands are in math mode
    - Escapes LaTeX special chars in non-math, non-code
    """
    import re

    # Split into code fences so we don't touch code blocks
    fence_pat = re.compile(r"(?s)(```.*?```)")
    parts = fence_pat.split(md)

    def _normalize_math_delims(text: str) -> str:
        # Convert \(...\) -> $...$ and \[...\] -> $$...$$
        text = re.sub(r"\\\((.*?)\\\)", r"$\1$", text, flags=re.S)
        text = re.sub(r"\\\[(.*?)\\\]", r"$$\1$$", text, flags=re.S)

        # Ensure there is no mix of $$ inside inline runs; leave $$...$$ alone
        return text

    def _force_math_for_cmds(text: str) -> str:
        # If a line contains a math command but no $ or $$, wrap the minimal span in $...$
        out_lines = []
        for ln in text.splitlines():
            if "$" in ln or "$$" in ln:
                out_lines.append(ln)
                continue
            if re.search(rf"\\{MATH_CMDS}\b", ln):
                out_lines.append(f"${ln}$")
            else:
                out_lines.append(ln)
        return "\n".join(out_lines)

    def _escape_latex_specials(text: str) -> str:
        # Do not escape inside math ($...$ or $$...$$). Split by math spans first.
        # Order: $$...$$ first (display), then $...$ (inline)
        def esc(s: str) -> str:
            # Escape: \, {, }, $, &, #, _, %, ~, ^
            s = s.replace("\\", r"\\")
            s = s.replace("{", r"\{").replace("}", r"\}")
            s = s.replace("&", r"\&").replace("#", r"\#").replace("%", r"\%")
            s = s.replace("_", r"\_").replace("$", r"\$")
            s = s.replace("~", r"\textasciitilde{}").replace("^", r"\textasciicircum{}")
            return s

        # Split on $$...$$
        disp_split = re.split(r"(\$\$.*?\$\$)", text, flags=re.S)
        disp_out = []
        for chunk in disp_split:
            if chunk.startswith("$$") and chunk.endswith("$$"):
                disp_out.append(chunk)  # leave math unchanged
            else:
                # Now split this chunk on inline $...$
                inl_split = re.split(r"(\$.*?\$)", chunk, flags=re.S)
                for sub in inl_split:
                    if sub.startswith("$") and sub.endswith("$"):
                        disp_out.append(sub)  # inline math unchanged
                    else:
                        disp_out.append(esc(sub))
        return "".join(disp_out)

    def _balance_dollars(text: str) -> str:
        # Very conservative: if a line has an odd number of $ (and not $$),
        # append one $ at the end to balance. Skip lines already containing $$.
        fixed = []
        for ln in text.splitlines():
            if "$$" in ln:
                fixed.append(ln)
                continue
            if ln.count("$") % 2 == 1:
                fixed.append(ln + "$")
            else:
                fixed.append(ln)
        return "\n".join(fixed)

    out = []
    for i, part in enumerate(parts):
        if i % 2 == 1:
            # code fence: leave exactly as-is
            out.append(part)
        else:
            t = part
            t = _normalize_math_delims(t)
            t = _force_math_for_cmds(t)
            t = _escape_latex_specials(t)
            t = _balance_dollars(t)
            out.append(t)
    return "".join(out)


def markdown_to_pdf(md_text, output_path="output.pdf"):
    header_tex = r"""
\usepackage{amsmath,amssymb,mathtools}
\usepackage{unicode-math}
\usepackage{physics}
\usepackage{siunitx}
"""
    import tempfile, os

    with tempfile.NamedTemporaryFile(mode="w", suffix=".tex", delete=False) as hf:
        hf.write(header_tex)
        header_path = hf.name

    try:
        pypandoc.get_pandoc_version()
        pypandoc.convert_text(
            md_text,
            to="pdf",
            # ✅ switch away from gfm
            format="markdown+tex_math_dollars+raw_tex",
            outputfile=output_path,
            extra_args=[
                "--standalone",
                "--pdf-engine=xelatex",
                "--include-in-header",
                header_path,
                "-V",
                "geometry:margin=1in",
                "--log=build.log",
            ],
        )
    finally:
        try:
            os.remove(header_path)
        except:
            pass


def actually_fix_markdown(md):
    client = genai.Client()

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"Fix the syntax errors in the following markdown code, return only the markdown code: \n\n{md}",
    )

    return response.text[len("```markdown\n") : -3].strip()


def search_topic(topic, subtopics, grade_level, num_problems):
    try:
        # Get textbook packet
        pkt = find_textbook_packet(
            topic=topic,
            subtopics=subtopics,
            grade_level=grade_level,
            max_sections=len(subtopics) + 2,
            quiz_per_section=3,
            debug=False,  # prints HTTP status and body head
        )
        md = textbook_json_to_markdown(pkt)

        # Create practice problems
        problems = create_practice_problems(
            topic=topic,
            subtopics=subtopics,
            grade_level=grade_level,
            num_problems=num_problems,
            debug=False,
        )

        # Cleans practice problems into markdown format
        PAGEBREAK = "\n\n\\newpage\n\n"

        problems_questions = ["# Practice Problems", ""]
        problems_solutions = ["# Solutions", ""]
        problems_sources = ["# Sources", ""]

        for i, p in enumerate(problems, 1):
            q = strip_leading_numbering(p["question"])
            s = strip_leading_numbering(p["solution"])

            # Use headings for stable numbering (avoids Markdown ordered-list quirks with math blocks)
            problems_questions.append(f"## Problem {i}")
            problems_questions.append(q)
            problems_questions.append("")  # spacer

            problems_solutions.append(f"## Problem {i}")
            problems_solutions.append(s)
            problems_solutions.append("")

            problems_sources.append(
                f"- {p['source_title']} — {p['source_url']} | {p['license']}"
            )
        problems_sources.append("")

        problems_sources.append("")

        questions_md = "\n\n\n".join(problems_questions)
        solutions_md = "\n\n\n".join(problems_solutions)
        
        # --- textbook citations ---
        textbook_citations = pkt.get("citations") or []
        for url in textbook_citations:
            if isinstance(url, str) and url.strip():
                problems_sources.append(f"- {url.strip()}")

        # (Optional) de-duplicate identical lines while preserving order
        seen = set()
        deduped_sources = ["# Sources", ""]
        for line in problems_sources[2:]:
            if line not in seen:
                deduped_sources.append(line)
                seen.add(line)

        problems_sources = deduped_sources
        problems_sources.append("")  # trailing newline

        # Fixing markdown formatting
        # fixed_main_md = fix_markdown(md)  # your textbook part
        # # fixed_q_md    = ensure_math_mode(fix_markdown(questions_md))
        # # fixed_s_md    = ensure_math_mode(fix_markdown(solutions_md))
        # fixed_q_md    = fix_markdown(questions_md)
        # fixed_s_md    = fix_markdown(solutions_md)
        fixed_main_md = fix_markdown(md)
        fixed_q_md = fix_markdown(questions_md)
        fixed_s_md = fix_markdown(solutions_md)

        # Sanitize for LaTeX robustness
        fixed_main_md = sanitize_markdown_for_latex(fixed_main_md)
        fixed_q_md = sanitize_markdown_for_latex(fixed_q_md)
        fixed_s_md = sanitize_markdown_for_latex(fixed_s_md)
        # no need to run on sources

        # ----- Assemble final document with explicit breaks between blocks -----
        packet_md = (
            fixed_main_md
            + PAGEBREAK
            + fixed_q_md
            + PAGEBREAK
            + fixed_s_md
            + PAGEBREAK
            + sources_md
        )

        hashed_part = sha256(
            datetime.now().strftime("%d/%m/%YT%H:%M:%S").encode("utf-8")
        ).hexdigest()

        markdown_to_pdf(
            packet_md,
            output_path=f"{BASE_PATH}/static/pdfs/{topic}_Packet_for_{grade_level}_{hashed_part}.pdf",
        )
        fixed_packet_md = actually_fix_markdown(packet_md)

        open("test.md", "w").write(fixed_packet_md)

        # fixed_packet_md = fixed_packet_md.replace('\\$', '$')

        return f"{topic}_Packet_for_{grade_level}_{hashed_part}.pdf"

    except Exception as e:
        print("\n[FATAL]", e)
        return None


# Example usage:
# print(search_topic("Civil War", ["Slave Trade", "Abraham Lincoln", "Battle of Gettysburg"], "middle school", 3))
