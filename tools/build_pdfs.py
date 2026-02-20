#!/usr/bin/env python3
import argparse
import os
import re
from pathlib import Path

import markdown
from weasyprint import HTML, CSS


DEFAULT_EXCLUDE_DIRS = {"temp", "tmp", ".git", ".venv", "out", "__pycache__"}


def slugify_path(rel_path: Path) -> str:
    """
    Convert a relative path like 'cm1-td/td1.md' -> 'cm1-td_td1.pdf'
    while keeping it stable and readable.
    """
    s = str(rel_path).replace(os.sep, "_")
    s = re.sub(r"[^A-Za-z0-9._-]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s


def should_exclude(path: Path, exclude_dirs: set[str]) -> bool:
    # Exclude any file that is under excluded directories
    for part in path.parts:
        if part in exclude_dirs:
            return True
    return False


def md_to_html(md_text: str, title: str) -> str:
    """
    Markdown -> HTML document (full HTML) with a simple wrapper.
    Mermaid blocks are kept as code blocks (no rendering).
    """
    md = markdown.Markdown(
        extensions=[
            "tables",
            "fenced_code",
            "toc",
            "sane_lists",
            "smarty",
            "admonition",
            "pymdownx.superfences",
            "pymdownx.details",
            "pymdownx.tasklist",
            "pymdownx.highlight",
        ],
        extension_configs={
            "pymdownx.tasklist": {"custom_checkbox": True},
            "pymdownx.highlight": {"use_pygments": False},
        },
        output_format="html5",
    )

    body = md.convert(md_text)

    # Ensure code fences with "mermaid" remain readable
    # (markdown produces <pre><code class="language-mermaid">...</code></pre>)
    # We just leave it as-is; no diagram rendering.

    return f"""<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{escape_html(title)}</title>
</head>
<body>
{body}
</body>
</html>
"""


def escape_html(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def build_pdf(md_path: Path, out_dir: Path, css_path: Path, base_dir: Path) -> Path:
    rel = md_path.relative_to(base_dir)
    pdf_name = slugify_path(rel.with_suffix("")) + ".pdf"
    out_path = out_dir / pdf_name
    out_path.parent.mkdir(parents=True, exist_ok=True)

    md_text = md_path.read_text(encoding="utf-8")
    title = rel.as_posix()

    html_text = md_to_html(md_text, title=title)

    # base_url is critical: it allows relative links/images to resolve
    HTML(string=html_text, base_url=str(md_path.parent)).write_pdf(
        str(out_path),
        stylesheets=[CSS(filename=str(css_path))],
    )
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Build PDFs from Markdown files.")
    parser.add_argument("--root", default=".", help="Repository root (default: .)")
    parser.add_argument("--out", default="out/pdfs", help="Output folder for PDFs")
    parser.add_argument("--css", default="assets/pdf.css", help="CSS file for PDF styling")
    parser.add_argument(
        "--include-readme",
        action="store_true",
        help="Also convert the root README.md",
    )
    args = parser.parse_args()

    base_dir = Path(args.root).resolve()
    out_dir = (base_dir / args.out).resolve()
    css_path = (base_dir / args.css).resolve()

    if not css_path.exists():
        raise SystemExit(f"CSS not found: {css_path}")

    include_dirs = [
        base_dir / "cm1-td",
        base_dir / "cm2-td",
        base_dir / "cm3-td",
    ]
    top_level = [base_dir / "CM1.md", base_dir / "CM2.md", base_dir / "CM3.md"]

    candidates: list[Path] = []
    for p in top_level:
        if p.exists():
            candidates.append(p)

    for d in include_dirs:
        if d.exists() and d.is_dir():
            candidates.extend(sorted(d.glob("*.md")))

    if args.include_readme:
        readme = base_dir / "README.md"
        if readme.exists():
            candidates.append(readme)

    exclude_dirs = set(DEFAULT_EXCLUDE_DIRS) | {"temp", "tmp"}
    converted = 0

    print(f"Root      : {base_dir}")
    print(f"CSS       : {css_path}")
    print(f"Output dir: {out_dir}")
    print("")

    for md_file in candidates:
        if should_exclude(md_file.relative_to(base_dir), exclude_dirs):
            continue
        if md_file.suffix.lower() != ".md":
            continue

        try:
            out_pdf = build_pdf(md_file, out_dir, css_path, base_dir)
            converted += 1
            print(f"[OK] {md_file.relative_to(base_dir)} -> {out_pdf.relative_to(base_dir)}")
        except Exception as e:
            print(f"[ERR] {md_file.relative_to(base_dir)}: {e}")

    print("")
    print(f"Done. PDFs generated: {converted}")


if __name__ == "__main__":
    main()
