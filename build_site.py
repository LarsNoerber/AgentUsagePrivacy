import argparse
import html
import json
import re
import shutil
import unicodedata
import datetime
from pathlib import Path


def render_paragraphs(text: str) -> str:
    pattern = re.compile(r"https?://[^\s<>]+|[A-Za-z0-9_.+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
    blocks = []
    for paragraph in text.split("\n\n"):
        pieces = []
        cursor = 0
        for match in pattern.finditer(paragraph):
            pieces.append(html.escape(paragraph[cursor:match.start()]))
            token = match.group().rstrip(".,;)")
            suffix = match.group()[len(token):]
            href = token if token.startswith("https://") or token.startswith("http://") else "mailto:" + token
            pieces.append(f'<a href="{html.escape(href, quote=True)}">{html.escape(token)}</a>{html.escape(suffix)}')
            cursor = match.end()
        pieces.append(html.escape(paragraph[cursor:]))
        if paragraph.strip():
            blocks.append("<p>" + "".join(pieces) + "</p>")
    return "\n".join(blocks)


def slug(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", normalized).strip("-") or "section"


def privacy_sections(data: dict) -> list[dict]:
    sections = data.get("privacySections", [])
    if sections:
        return sections
    return [{"title": "Privacy policy", "body": data.get("privacy", "")}]


def policy_for_publication(policy: dict) -> dict:
    published = json.loads(json.dumps(policy))
    for language in ("de", "en"):
        data = published[language]
        data["privacy"] = "\n\n".join(
            f"{section['title']}\n{section['body']}" for section in privacy_sections(data)
        )
    return published


def validate_policy(policy: dict) -> dict:
    if policy.get("schema") != 1 or not isinstance(policy.get("policyRevision"), int) or policy["policyRevision"] < 1:
        raise ValueError("Policy needs schema 1 and a positive policyRevision")
    datetime.date.fromisoformat(policy["updatedAt"])
    for language in ("de", "en"):
        data = policy[language]
        sections = privacy_sections(data)
        if not sections or any(not isinstance(s.get("title"), str) or not s["title"].strip()
                               or not isinstance(s.get("body"), str) or not s["body"].strip() for s in sections):
            raise ValueError("Every policy section needs a title and body")
        anchors = [slug(section["title"]) for section in sections]
        if len(anchors) != len(set(anchors)):
            raise ValueError("Policy section anchors must be unique")
    published = policy_for_publication(policy)
    for language in ("de", "en"):
        for key in ("imprint", "privacy", "rights"):
            body = published[language][key]
            if not isinstance(body, str) or not body.strip() or len(body) > 24000:
                raise ValueError(f"{language}/{key} exceeds the Android policy format")
    if len((json.dumps(published, ensure_ascii=False, indent=2) + "\n").encode("utf-8")) > 131072:
        raise ValueError("Published JSON exceeds the Android download limit")
    return published


def render_page(policy: dict, language: str, base: str) -> str:
    de = language == "de"
    title = "Datenschutzerklärung und Impressum" if de else "Privacy policy and publisher information"
    imprint = "Impressum" if de else "Publisher information"
    rights = "Deine Rechte" if de else "Your rights"
    updated = "Stand" if de else "Last updated"
    switch_de = "Deutsch" if de else "German"
    switch_en = "Englisch" if de else "English"
    footer = (
        "AgentMeter ist eine unabhängige App. Anbieternamen bezeichnen unterstützte Dienste."
        if de
        else "AgentMeter is an independent app. Provider names identify supported services."
    )
    data = policy[language]
    content_nav = [
        ("imprint", imprint),
        *((f"privacy-{slug(section['title'])}", section["title"]) for section in privacy_sections(data)),
        ("rights", rights),
    ]
    toc = "\n".join(f'<a href="#{anchor}">{html.escape(label)}</a>' for anchor, label in content_nav)
    privacy_html = "\n".join(
        f'<section aria-labelledby="privacy-{slug(section["title"])}">'
        f'<h2 id="privacy-{slug(section["title"])}">{html.escape(section["title"])}</h2>'
        f'{render_paragraphs(section["body"])}</section>'
        for section in privacy_sections(data)
    )
    return f'''<!doctype html>
<html lang="{language}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="index,follow">
  <title>AgentMeter — {title}</title>
  <meta name="description" content="AgentMeter privacy policy and publisher information">
  <style>
    :root {{ color-scheme: dark; font-family: Inter, ui-sans-serif, system-ui, sans-serif; line-height: 1.7; background: #07121f; color: #eaf3ff; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: radial-gradient(ellipse at 15% 0%, #183653 0, transparent 45%), radial-gradient(ellipse at 95% 20%, #23234d 0, transparent 38%), #07121f; min-height: 100vh; }}
    main {{ max-width: 56rem; margin: 0 auto; padding: 2.25rem 1.2rem 4rem; }}
    header {{ padding: 1.5rem 0 2rem; }}
    footer {{ color: #a9bad0; text-align: center; padding: 1.6rem 0; font-size: .9rem; }}
    nav {{ display: flex; flex-wrap: wrap; gap: .6rem; margin: 1.4rem 0 2rem; }}
    nav a {{ display: inline-block; padding: .4rem .85rem; border: 1px solid #46607b; border-radius: 999px; background: #112236; text-decoration: none; }}
    .contents {{ margin: 0 0 2rem; padding: 1rem; border: 1px solid #ffffff18; border-radius: .8rem; background: #101c2bee; }}
    .contents strong {{ display: block; margin-bottom: .6rem; }}
    .contents a {{ padding: .2rem .4rem; font-size: .92rem; }}
    .brand {{ display: flex; align-items: center; gap: .75rem; font-size: 1.1rem; font-weight: 750; letter-spacing: .02em; }}
    .brand img {{ width: 2.8rem; height: 2.8rem; border: 1px solid #ffffff22; border-radius: .8rem; box-shadow: 0 8px 24px #0005; }}
    .eyebrow {{ color: #6bd8ff; text-transform: uppercase; letter-spacing: .14em; font-size: .76rem; font-weight: 700; margin-top: 2rem; }}
    a {{ color: #78d8ff; }}
    h1, h2 {{ line-height: 1.25; }}
    h1 {{ font-size: clamp(2rem, 6vw, 3rem); margin: .35rem 0; letter-spacing: -.035em; }}
    h2 {{ font-size: 1.35rem; margin: 0 0 1rem; }}
    .updated {{ color: #a9bad0; margin: .5rem 0; }}
    section {{ margin: 1.1rem 0; padding: clamp(1.15rem, 4vw, 1.8rem); border: 1px solid #ffffff18; border-radius: 1.2rem; background: linear-gradient(145deg, #14263aee, #101c2bee); box-shadow: 0 16px 42px #0002; }}
    section p {{ margin: 0 0 1rem; color: #d4e1f0; }}
    section p:last-child {{ margin-bottom: 0; }}
    p {{ overflow-wrap: anywhere; }}
    :focus-visible {{ outline: 3px solid #ffcc66; outline-offset: 3px; }}
    @media (max-width: 520px) {{ main {{ padding-top: 1rem; }} header {{ padding-top: .8rem; }} }}
  </style>
</head>
<body>
  <main>
    <header>
      <div class="brand"><img src="{base}assets/agentmeter.png" alt=""><span>AgentMeter</span></div>
      <nav aria-label="Language">
        <a href="{base}de/" lang="de">{switch_de}</a>
        <a href="{base}en/" lang="en">{switch_en}</a>
      </nav>
      <h1>{title}</h1>
      <p class="eyebrow">AgentMeter · Legal</p>
      <p class="updated">{updated}: {html.escape(policy['updatedAt'])}</p>
    </header>
    <nav class="contents" aria-label="{('Inhalt' if de else 'Contents')}"><strong>{('Auf dieser Seite' if de else 'On this page')}</strong>{toc}</nav>
    <section aria-labelledby="imprint"><h2 id="imprint">{imprint}</h2>{render_paragraphs(data['imprint'])}</section>
    {privacy_html}
    <section aria-labelledby="rights"><h2 id="rights">{rights}</h2>{render_paragraphs(data['rights'])}</section>
    <footer><p>{footer}</p></footer>
  </main>
</body>
</html>
'''


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    source = Path(__file__).parent
    output = Path(args.output_dir)
    policy = json.loads((source / "policy.json").read_text(encoding="utf-8"))
    published = validate_policy(policy)
    output.mkdir(parents=True, exist_ok=True)
    (output / "assets").mkdir(exist_ok=True)
    (output / "policy.json").write_text(json.dumps(published, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    shutil.copy2(source / "assets" / "agentmeter.png", output / "assets" / "agentmeter.png")
    (output / "de").mkdir(exist_ok=True)
    (output / "en").mkdir(exist_ok=True)
    (output / "de" / "index.html").write_text(render_page(policy, "de", "../"), encoding="utf-8")
    (output / "en" / "index.html").write_text(render_page(policy, "en", "../"), encoding="utf-8")
    (output / "index.html").write_text('''<!doctype html>
<html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>AgentMeter — Privacy policy</title><style>:root{font:1.05rem/1.6 system-ui;background:#07121f;color:#eaf3ff}body{max-width:48rem;margin:0 auto;padding:12vh 1.2rem;background:radial-gradient(ellipse at top left,#183653,transparent 60%)}.brand{display:flex;align-items:center;gap:.8rem;font-size:1.2rem;font-weight:700}.brand img{width:3rem;border-radius:.8rem}h1{font-size:clamp(2rem,7vw,3rem);line-height:1.1}section{margin-top:2rem;padding:1.5rem;border:1px solid #ffffff20;border-radius:1.2rem;background:#14263a}a{display:inline-block;margin:.5rem .5rem 0 0;padding:.55rem 1rem;border:1px solid #46607b;border-radius:999px;color:#78d8ff;text-decoration:none}</style></head>
<body><main><div class="brand"><img src="assets/agentmeter.png" alt=""><span>AgentMeter</span></div><section><h1>Datenschutz<br>Privacy</h1><p>Sprache wählen / Choose a language:</p><a href="de/" lang="de">Deutsch</a><a href="en/" lang="en">English</a></section></main></body></html>''', encoding="utf-8")


if __name__ == "__main__":
    main()
