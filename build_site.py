import argparse
import html
import json
import shutil
from pathlib import Path


def render_paragraphs(text: str) -> str:
    email = "codlNg@gmx.de"
    complaint = "https://datenschutz.hessen.de/service/beschwerde-uebermitteln"
    blocks = []
    for paragraph in text.split("\n\n"):
        escaped = html.escape(paragraph.strip())
        escaped = escaped.replace(email, f'<a href="mailto:{email}">{email}</a>')
        escaped = escaped.replace(complaint, f'<a href="{complaint}">{html.escape(complaint)}</a>')
        escaped = escaped.replace(
            "https://openrouter.ai/api/v1/key",
            '<a href="https://openrouter.ai/api/v1/key">https://openrouter.ai/api/v1/key</a>',
        )
        if escaped:
            blocks.append(f"<p>{escaped}</p>")
    return "\n".join(blocks)


def render_page(policy: dict, language: str, base: str) -> str:
    de = language == "de"
    title = "Datenschutzerklärung und Impressum" if de else "Privacy policy and publisher information"
    imprint = "Impressum" if de else "Publisher information"
    privacy = "Datenschutzerklärung" if de else "Privacy policy"
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
    <section aria-labelledby="imprint"><h2 id="imprint">{imprint}</h2>{render_paragraphs(data['imprint'])}</section>
    <section aria-labelledby="privacy"><h2 id="privacy">{privacy}</h2>{render_paragraphs(data['privacy'])}</section>
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
    if policy.get("schema") != 1 or not policy.get("updatedAt"):
        raise SystemExit("Unsupported or incomplete privacy policy schema")
    output.mkdir(parents=True, exist_ok=True)
    (output / "assets").mkdir(exist_ok=True)
    (output / "policy.json").write_text(json.dumps(policy, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
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
