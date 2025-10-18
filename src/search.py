import os
import json
import requests
from hashlib import sha256
import pathlib
from dotenv import load_dotenv
from datetime import datetime
import re
import pypandoc

load_dotenv()

BASE_PATH = pathlib.Path(__file__).parent

PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")


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


def assert_api_key():
    if not PERPLEXITY_API_KEY or PERPLEXITY_API_KEY.strip() == "":
        raise RuntimeError("PERPLEXITY_API_KEY is missing or empty")


########################################################################################
# ----------------- Generates Textbook-style Lessons -----------------
########################################################################################


def create_lesson(messages, *, temperature=0.2, max_tokens=8000, debug=True):
    assert_api_key()
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "content-type": "application/json",
    }
    payload = {
        "model": "sonar-pro",  # try "sonar" if you get 400 / access errors
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

    # Explicitly raise HTTP errors so you see body in console
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
    },
}

SYSTEM_MSG = (
    "You are a master educator. Write like a concise textbook: clean, precise, structured. "
    "Short paragraphs (plain text), minimal jargon, clear notation. "
    "No citations, links, or markdown. Return ONLY valid JSON."
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
- Each section: 120–220 word overview, 3–6 key points, essential formulas (LaTeX ok),
  1 worked example with steps, 1 small diagram described by text (caption + drawing instructions),
  2–4 common pitfalls, and {quiz_per_section} mini-quiz Q/A.
- Keep derivations brief (5–10 lines) only when essential.
- DO NOT include citations, URLs, references, or markdown.
- Keep total number of sections ≤ {max_sections} by merging closely related subtopics.

Output:
Return ONLY valid JSON matching this schema (no prose outside JSON):
{json.dumps(SCHEMA_HINT)}
""".strip()

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
Avoid: paywalled sites, copyrighted textbooks without open licenses, commercial worksheets.
"""


def build_messages(topic, subtopics, grade_level, num_problems):
    subtopics_txt = ", ".join(subtopics) if subtopics else "—"
    today = datetime.utcnow().date().isoformat()

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
        "return_search_results": True,  # helpful for auditing sources
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


def fix_markdown(markdown):
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
                "content": "Ignore any previous math formatting instructions. "
                "Always output inline math expressions wrapped in single dollar signs `$...$`. "
                "For display math use `$$...$$`. "
                "Do not search the web, only process and reformat text provided by the user.",
            },
            {
                "role": "user",
                "content": f"Reformat the following text into correctly formatted markdown code. Format it such that the equations are centered on the page and are easy to identify and read. Only return the markdown code. Do not use HTML:\n\n{markdown}.",
            },
        ],
        "max_tokens": 16000,
        "temperature": 0.3,
    }

    response = requests.post(PERPLEXITY_API_URL, headers=headers, json=payload)
    return response.json()["choices"][0]["message"]["content"][
        len("```markdown\n") : -3
    ]


# commands that must be inside math mode
_MATH_CMDS = r"(vec|frac|cdot|times|ldots|nabla|partial|sqrt|sum|prod|int|lim|log|ln|sin|cos|tan|alpha|beta|gamma|Delta|leq|geq|pm)"


def ensure_math_mode(md: str) -> str:
    lines, out = md.splitlines(), []
    for ln in lines:
        # already math? skip
        if any(
            tok in ln
            for tok in (
                "\\[",
                "\\]",
                "\\(",
                "\\)",
                "$",
                "\\begin{align",
                "\\begin{equation}",
            )
        ):
            out.append(ln)
            continue

        # contains math commands but no math delimiters → wrap whole line
        if re.search(rf"\\{_MATH_CMDS}\\b", ln):
            ln = f"${ln}$"

        # fix common artifacts (e.g., '\$.' should be '$.')
        ln = ln.replace("\\$.", "$.")
        ln = ln.replace("\\$", "$")

        # balance odd number of $ (rare, but prevents LaTeX choke)
        if ln.count("$") % 2 == 1:
            ln += "$"

        out.append(ln)
    return "\n".join(out)


def markdown_to_pdf(md_text, output_path="output.pdf"):
    pypandoc.get_pandoc_version()
    pypandoc.convert_text(
        md_text,  # <-- use the argument
        to="pdf",
        format="markdown+raw_tex+tex_math_dollars+tex_math_single_backslash",
        outputfile=output_path,
        extra_args=[
            "--standalone",
            "-V",
            "geometry:margin=1in",
            "--pdf-engine=xelatex",  # unicode-safe
        ],
    )


################################ Example usage ##########################################
if __name__ == "__main__":
    topic = "Python"
    subtopics = ["Loops", "Functions", "OOP"]
    file = "python.pdf"
    try:
        pkt = find_textbook_packet(
            topic=topic,
            subtopics=subtopics,
            grade_level="undergraduate",
            max_sections=6,
            quiz_per_section=3,
            debug=True,  # prints HTTP status and body head
        )
        md = textbook_json_to_markdown(pkt)
        fixed_md = fix_markdown(md)
        # print(f"\n\n####################################\n\n{fixed_md}")
        #### default, change later
        problems = create_practice_problems(
            topic=topic,
            subtopics=subtopics,
            grade_level="undergrad",
            num_problems=5,
        )

        PAGEBREAK = "\n\n\\newpage\n\n"  # blank lines around are important

        problems_questions = ["# Practice Problems", ""]
        problems_solutions = ["# Solutions", ""]
        problems_sources = ["# Sources", ""]

        for i, p in enumerate(problems, 1):
            # Use proper headings; no '---' lines (those create <hr/>)
            problems_questions.append(p["question"].rstrip())
            problems_questions.append("")  # blank line to end block

            problems_solutions.append(f"## Problem {i}")
            problems_solutions.append(p["solution"].rstrip())
            problems_solutions.append("")

            problems_sources.append(
                f"- {p['source_title']} — {p['source_url']} | {p['license']}"
            )
        problems_sources.append("")

        problems_sources.append("")  # trailing newline

        questions_md = "\n\n\n".join(problems_questions)
        solutions_md = "\n\n\n".join(problems_solutions)
        sources_md = "\n".join(problems_sources)

        # ----- Apply your fixer only to content, not page-break tokens -----
        fixed_main_md = fix_markdown(md)  # your textbook part
        fixed_q_md = ensure_math_mode(fix_markdown(questions_md))
        fixed_s_md = ensure_math_mode(fix_markdown(solutions_md))
        # DO NOT run the fixer over `sources_md` if it tends to strip list items or links.
        fixed_sources_md = sources_md

        # ----- Assemble final document with explicit breaks between blocks -----
        packet_md = (
            fixed_main_md
            + PAGEBREAK
            + fixed_q_md
            + PAGEBREAK
            + fixed_s_md
            + PAGEBREAK
            + fixed_sources_md
        )

        with open("Vectors_Packet.md", "w", encoding="utf-8") as f:
            f.write(packet_md)

        markdown_to_pdf(packet_md, output_path="Vectors_Packet.pdf")

    except Exception as e:
        print("\n[FATAL]", e)


def search_topic(topic, subtopics, grade_level, num_problems):
    try:
        # Get textbook packet
        pkt = find_textbook_packet(
            topic=topic,
            subtopics=subtopics,
            grade_level=grade_level,
            max_sections=len(subtopics) + 2,
            quiz_per_section=3,
            debug=True,  # prints HTTP status and body head
        )
        md = textbook_json_to_markdown(pkt)

        # Create practice problems
        problems = create_practice_problems(
            topic=topic,
            subtopics=subtopics,
            grade_level=grade_level,
            num_problems=num_problems,
        )

        # Cleans practice problems into markdown format
        PAGEBREAK = "\n\n\\newpage\n\n"

        problems_questions = ["# Practice Problems", ""]
        problems_solutions = ["# Solutions", ""]
        problems_sources = ["# Sources", ""]

        for i, p in enumerate(problems, 1):
            problems_questions.append(p["question"].rstrip())
            problems_questions.append("")

            problems_solutions.append(f"## Problem {i}")
            problems_solutions.append(p["solution"].rstrip())
            problems_solutions.append("")

            problems_sources.append(
                f"- {p['source_title']} — {p['source_url']} | {p['license']}"
            )
        problems_sources.append("")

        problems_sources.append("")

        questions_md = "\n\n\n".join(problems_questions)
        solutions_md = "\n\n\n".join(problems_solutions)
        sources_md = "\n".join(problems_sources)

        # Fixing markdown formatting
        fixed_main_md = fix_markdown(md)  # your textbook part
        fixed_q_md = ensure_math_mode(fix_markdown(questions_md))
        fixed_s_md = ensure_math_mode(fix_markdown(solutions_md))
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

        return f"{topic}_Packet_for_{grade_level}_{hashed_part}.pdf"

    except Exception as e:
        print("\n[FATAL]", e)
        return None
