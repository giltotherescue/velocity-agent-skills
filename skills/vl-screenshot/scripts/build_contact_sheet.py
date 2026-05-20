#!/usr/bin/env python3
"""Build a clickable screenshot contact sheet for feature review."""

from __future__ import annotations

import argparse
import html
import json
import subprocess
import zipfile
from pathlib import Path


def human_title(path: Path) -> str:
    stem = path.stem
    parts = stem.split("-", 1)

    if len(parts) == 2 and parts[0].isdigit():
        return f"{int(parts[0])}. {parts[1].replace('-', ' ').title()}"

    return stem.replace("-", " ").replace("_", " ").title()


def human_size(path: Path) -> str:
    size = path.stat().st_size
    units = ["B", "KB", "MB", "GB"]

    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.1f} {unit}" if unit != "B" else f"{size} {unit}"

        size /= 1024

    return f"{size} B"


def create_zip(images: list[Path], output: Path) -> Path | None:
    if not images:
        output.unlink(missing_ok=True)
        return None

    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for image in images:
            archive.write(image, arcname=image.name)

    return output


def build_html(
    images: list[Path],
    title: str,
    subtitle: str,
    columns: int,
    zip_path: Path | None,
) -> str:
    cards = []
    viewer_items = []

    for index, image in enumerate(images):
        name = image.name
        label = human_title(image)
        viewer_items.append({"src": name, "title": label})
        cards.append(
            f"""<section class="shot">
  <h2>{html.escape(label)}</h2>
  <button class="shot-button" type="button" data-index="{index}" aria-label="Open {html.escape(label)}">
    <img src="{html.escape(name)}" alt="{html.escape(label)}">
  </button>
</section>"""
        )

    empty = ""
    if not images:
        empty = '<p class="empty">No screenshots matched the selected pattern.</p>'

    download = ""
    if zip_path is not None:
        download = f"""<a class="download" href="{html.escape(zip_path.name)}" download>
      Download screenshots zip <span>{html.escape(human_size(zip_path))}</span>
    </a>"""

    safe_title = html.escape(title)
    safe_subtitle = html.escape(subtitle)
    safe_columns = max(1, min(columns, 4))
    viewer_json = json.dumps(viewer_items).replace("</", "<\\/")

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{safe_title}</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f5f6f8;
      --card: #ffffff;
      --text: #111827;
      --muted: #5b6472;
      --line: #e5e7eb;
      --shadow: 0 12px 30px rgba(15, 23, 42, 0.08);
    }}

    * {{ box-sizing: border-box; }}

    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font: 16px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}

    header {{
      padding: 32px 40px 8px;
    }}

    h1 {{
      margin: 0 0 8px;
      font-size: 28px;
      line-height: 1.15;
    }}

    p {{
      margin: 0;
      color: var(--muted);
    }}

    .topbar {{
      display: flex;
      align-items: end;
      justify-content: space-between;
      gap: 20px;
    }}

    .download {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      flex: 0 0 auto;
      padding: 10px 14px;
      color: #ffffff;
      background: #111827;
      border-radius: 8px;
      text-decoration: none;
      font-size: 14px;
      font-weight: 700;
    }}

    .download span {{
      color: #cbd5e1;
      font-weight: 600;
    }}

    main {{
      display: grid;
      grid-template-columns: repeat({safe_columns}, minmax(0, 1fr));
      gap: 24px;
      padding: 28px 40px 48px;
    }}

    .shot {{
      overflow: hidden;
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 12px;
      box-shadow: var(--shadow);
    }}

    h2 {{
      margin: 0;
      padding: 12px 14px;
      border-bottom: 1px solid #eceff3;
      font-size: 14px;
      line-height: 1.3;
    }}

    .shot-button {{
      display: block;
      width: 100%;
      padding: 0;
      background: #eef1f5;
      border: 0;
      cursor: zoom-in;
    }}

    img {{
      display: block;
      width: 100%;
      height: auto;
    }}

    .empty {{
      grid-column: 1 / -1;
      padding: 24px;
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 12px;
    }}

    .viewer {{
      position: fixed;
      inset: 0;
      z-index: 20;
      display: none;
      grid-template-rows: auto 1fr;
      background: rgba(15, 23, 42, 0.94);
      color: #ffffff;
    }}

    .viewer[data-open="true"] {{
      display: grid;
    }}

    .viewer-bar {{
      display: grid;
      grid-template-columns: auto 1fr auto;
      align-items: center;
      gap: 12px;
      padding: 14px 18px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.16);
    }}

    .viewer-title {{
      min-width: 0;
      font-size: 14px;
      font-weight: 700;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }}

    .viewer-actions {{
      display: flex;
      gap: 8px;
    }}

    .viewer button {{
      padding: 8px 11px;
      color: #ffffff;
      background: rgba(255, 255, 255, 0.12);
      border: 1px solid rgba(255, 255, 255, 0.24);
      border-radius: 8px;
      cursor: pointer;
      font: inherit;
      font-size: 13px;
      font-weight: 700;
    }}

    .viewer button:hover {{
      background: rgba(255, 255, 255, 0.2);
    }}

    .viewer-frame {{
      min-height: 0;
      overflow: auto;
      padding: 24px;
    }}

    .viewer-frame img {{
      width: min(100%, 1400px);
      margin: 0 auto;
      background: #ffffff;
      box-shadow: 0 24px 80px rgba(0, 0, 0, 0.34);
    }}

    @media (max-width: 900px) {{
      header {{
        padding: 24px 20px 0;
      }}

      .topbar {{
        align-items: stretch;
        flex-direction: column;
      }}

      .download {{
        justify-content: center;
      }}

      main {{
        grid-template-columns: 1fr;
        padding: 20px;
      }}

      .viewer-bar {{
        grid-template-columns: 1fr;
      }}

      .viewer-actions {{
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
      }}

      .viewer-frame {{
        padding: 14px;
      }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="topbar">
      <div>
        <h1>{safe_title}</h1>
        <p>{safe_subtitle}</p>
      </div>
      {download}
    </div>
  </header>
  <main>
    {empty}
    {"".join(cards)}
  </main>
  <section class="viewer" id="viewer" aria-hidden="true">
    <div class="viewer-bar">
      <div class="viewer-title" id="viewerTitle"></div>
      <div></div>
      <div class="viewer-actions">
        <button type="button" id="viewerPrev">Previous</button>
        <button type="button" id="viewerNext">Next</button>
        <button type="button" id="viewerClose">Close</button>
      </div>
    </div>
    <div class="viewer-frame">
      <img id="viewerImage" src="" alt="">
    </div>
  </section>
  <script>
    const screenshots = {viewer_json};
    const viewer = document.getElementById("viewer");
    const viewerTitle = document.getElementById("viewerTitle");
    const viewerImage = document.getElementById("viewerImage");
    const viewerPrev = document.getElementById("viewerPrev");
    const viewerNext = document.getElementById("viewerNext");
    const viewerClose = document.getElementById("viewerClose");
    let currentIndex = 0;

    function openViewer(index) {{
      if (!screenshots.length) {{
        return;
      }}

      currentIndex = (index + screenshots.length) % screenshots.length;
      const shot = screenshots[currentIndex];
      viewerTitle.textContent = `${{currentIndex + 1}} / ${{screenshots.length}} - ${{shot.title}}`;
      viewerImage.src = shot.src;
      viewerImage.alt = shot.title;
      viewer.dataset.open = "true";
      viewer.setAttribute("aria-hidden", "false");
    }}

    function closeViewer() {{
      viewer.dataset.open = "false";
      viewer.setAttribute("aria-hidden", "true");
      viewerImage.src = "";
    }}

    document.querySelectorAll(".shot-button").forEach((button) => {{
      button.addEventListener("click", () => openViewer(Number(button.dataset.index)));
    }});

    viewerPrev.addEventListener("click", () => openViewer(currentIndex - 1));
    viewerNext.addEventListener("click", () => openViewer(currentIndex + 1));
    viewerClose.addEventListener("click", closeViewer);

    viewer.addEventListener("click", (event) => {{
      if (event.target === viewer) {{
        closeViewer();
      }}
    }});

    document.addEventListener("keydown", (event) => {{
      if (viewer.dataset.open !== "true") {{
        return;
      }}

      if (event.key === "Escape") {{
        closeViewer();
      }} else if (event.key === "ArrowLeft") {{
        openViewer(currentIndex - 1);
      }} else if (event.key === "ArrowRight") {{
        openViewer(currentIndex + 1);
      }}
    }});
  </script>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Build an index.html screenshot contact sheet.")
    parser.add_argument("directory", help="Directory containing screenshots")
    parser.add_argument("--title", default="Feature Screenshot Review")
    parser.add_argument("--subtitle", default="Full flow screenshots. Click any image for detail.")
    parser.add_argument("--pattern", default="*.png")
    parser.add_argument("--columns", type=int, default=2)
    parser.add_argument("--zip-name", default="screenshots.zip")
    parser.add_argument("--no-zip", action="store_true", help="Do not create a downloadable screenshots zip")
    parser.add_argument("--open", action="store_true", help="Open the generated index.html")

    args = parser.parse_args()
    directory = Path(args.directory).expanduser().resolve()
    directory.mkdir(parents=True, exist_ok=True)

    images = sorted(
        [path for path in directory.glob(args.pattern) if path.is_file()],
        key=lambda path: path.name,
    )

    zip_path = None
    if not args.no_zip:
        zip_path = create_zip(images, directory / args.zip_name)

    output = directory / "index.html"
    output.write_text(
        build_html(images, args.title, args.subtitle, args.columns, zip_path),
        encoding="utf-8",
    )

    print(output)
    if zip_path is not None:
        print(zip_path)

    if args.open:
        subprocess.run(["open", str(output)], check=False)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
