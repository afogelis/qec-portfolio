"""Regenerate the portfolio landing README from ``portfolio.toml``.

The README keeps a few hand-written prose sections (intro, reading order, quick
start). Everything that lists projects -- the repository tables, the dependency
graph, the test-status list and the write-up index -- is generated from the
manifest and injected between ``<!-- BEGIN:key -->`` / ``<!-- END:key -->``
markers. This keeps a single source of truth so the page cannot drift as new
projects are added.

Usage::

    python scripts/build_portfolio_index.py            # rewrite README.md
    python scripts/build_portfolio_index.py --check     # fail if out of date

The manifest is intentionally topic-neutral (projects carry an ``area``), so the
same generator handles a multi-subject research portfolio, not just QEC.
"""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "portfolio.toml"
README = ROOT / "README.md"


def load_manifest() -> dict:
    with MANIFEST.open("rb") as handle:
        return tomllib.load(handle)


def repo_url(user: str, name: str) -> str:
    return f"https://github.com/{user}/{name}"


def _projects_by_area(data: dict) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for project in data["project"]:
        grouped.setdefault(project["area"], []).append(project)
    return grouped


def render_repositories(data: dict) -> str:
    user = data["meta"]["github_user"]
    tiers = data["tier"]
    areas = data["area"]
    by_area = _projects_by_area(data)
    multi_area = sum(1 for a in areas if by_area.get(a["key"])) > 1

    area_level = "###" if multi_area else ""
    tier_level = "####" if multi_area else "###"

    lines: list[str] = []
    for area in areas:
        members = by_area.get(area["key"], [])
        if not members:
            continue
        if multi_area:
            lines.append(f"{area_level} {area['name']}")
            lines.append("")
            if area.get("intro"):
                lines.append(area["intro"].strip())
                lines.append("")
        for tier in tiers:
            tier_members = sorted(
                (p for p in members if p["tier"] == tier["key"]),
                key=lambda p: p["number"],
            )
            if not tier_members:
                continue
            lines.append(f"{tier_level} {tier['title']}")
            lines.append("")
            if tier.get("blurb"):
                lines.append(tier["blurb"])
                lines.append("")
            lines.append("| Repository | What it does | Highlight |")
            lines.append("|-----------|--------------|-----------|")
            for project in tier_members:
                url = repo_url(user, project["name"])
                lines.append(
                    f"| [`{project['name']}`]({url}) "
                    f"| {project['summary']} | {project['highlight']} |"
                )
            lines.append("")
    return "\n".join(lines).rstrip()


def render_graph(data: dict) -> str:
    number_of = {p["name"]: p["number"] for p in data["project"]}
    projects = sorted(data["project"], key=lambda p: p["number"])

    edges: list[str] = []
    connected: set[int] = set()
    labels: dict[int, str] = {p["number"]: p["name"] for p in projects}

    for project in projects:
        target = project["number"]
        for dep in project.get("deps", []):
            source = number_of[dep]
            edges.append(f"  P{source}[{labels[source]}] --> P{target}[{labels[target]}]")
            connected.update({source, target})
        for artifact in project.get("artifact_deps", []):
            dep_name, _, label = artifact.partition("|")
            dest = number_of[dep_name.strip()]
            edges.append(
                f"  P{target}[{labels[target]}] -.->|{label.strip()}| P{dest}[{labels[dest]}]"
            )
            connected.update({target, dest})

    standalone = [
        f"  P{p['number']}[{p['name']}]"
        for p in projects
        if p["number"] not in connected
    ]

    body = "\n".join(["flowchart TD", *edges, *standalone])
    return f"```mermaid\n{body}\n```"


def render_tests(data: dict) -> str:
    projects = sorted(data["project"], key=lambda p: p["number"])
    lines = [f"- {p['name']}: {p['tests']}" for p in projects]
    return "\n".join(lines)


def render_writeups(data: dict) -> str:
    lines = [
        "| # | Write-up | Markdown | Word |",
        "|---|----------|----------|------|",
        "| - | Portfolio overview "
        "| [md](writeups/md/00_portfolio_overview.md) "
        "| [docx](writeups/docx/00_portfolio_overview.docx) |",
    ]
    for project in sorted(data["project"], key=lambda p: p["number"]):
        slug = project["writeup_slug"]
        lines.append(
            f"| {project['number']} | {project['writeup_title']} "
            f"| [md](writeups/md/{slug}.md) "
            f"| [docx](writeups/docx/{slug}.docx) |"
        )
    return "\n".join(lines)


def render_summary(data: dict) -> str:
    by_area = _projects_by_area(data)
    focus = next((a for a in data["area"] if a.get("focus")), data["area"][0])
    count = len(by_area.get(focus["key"], []))
    return f"Current focus: **{focus['name']}** -- {count} projects."


def replace_block(text: str, key: str, body: str) -> str:
    begin = f"<!-- BEGIN:{key} -->"
    end = f"<!-- END:{key} -->"
    start = text.find(begin)
    stop = text.find(end)
    if start == -1 or stop == -1:
        raise SystemExit(f"missing markers for block '{key}' in README.md")
    head = text[: start + len(begin)]
    tail = text[stop:]
    return f"{head}\n{body}\n{tail}"


def build(text: str, data: dict) -> str:
    text = replace_block(text, "summary", render_summary(data))
    text = replace_block(text, "repositories", render_repositories(data))
    text = replace_block(text, "dependency-graph", render_graph(data))
    text = replace_block(text, "test-status", render_tests(data))
    text = replace_block(text, "writeups", render_writeups(data))
    return text


def main() -> None:
    check = "--check" in sys.argv[1:]
    data = load_manifest()
    current = README.read_text(encoding="utf-8")
    updated = build(current, data)

    if check:
        if current != updated:
            raise SystemExit("README.md is out of date; run scripts/build_portfolio_index.py")
        print("README.md is up to date.")
        return

    README.write_text(updated, encoding="utf-8")
    print(f"Regenerated README.md from {MANIFEST.name}.")


if __name__ == "__main__":
    main()
