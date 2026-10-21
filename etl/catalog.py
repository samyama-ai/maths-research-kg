"""Read the maths_research catalog: frontmatter, the ten sections, bullets and references."""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path

SECTION_RE = re.compile(r"^## (\d+)\.[^\n]*\n", re.MULTILINE)
BULLET_RE = re.compile(r"^[-*] ", re.MULTILINE)
LEAD_RE = re.compile(r"^\*\*([^*]{2,120}?)\*\*[:.]?")
DOI_RE = re.compile(r"\b10\.\d{4,9}/[^\s)>\]]+")
ARXIV_NEW_RE = re.compile(r"arXiv:\s?(\d{4}\.\d{4,5})(v\d+)?", re.IGNORECASE)
ARXIV_OLD_RE = re.compile(r"arXiv:\s?([a-z-]+(?:\.[A-Z]{2})?/\d{7})", re.IGNORECASE)
YEAR_RE = re.compile(r"\b(1[6-9]\d\d|20[0-3]\d)\b")
# Numbers that look like years but are not: URLs, DOIs, arXiv ids, page ranges, "Lecture Notes 1554".
NOT_YEAR_RE = re.compile(r"https?://\S+|\b10\.\d{4,9}/\S+|arXiv:\s?\S+|\b\d+\s?[–-]\s?\d+|(?:Notes|Vol\.?|Volume) in \w+ \d+|(?:Notes|Vol\.?|Volume)\s+\d+", re.IGNORECASE)
TAG_RE = re.compile(r"^- \*\*\[([^\]]+)\]\*\*\s*")
TITLE_RE = re.compile(r"(?<!\*)\*([^*]{3,300}?)\*(?!\*)")


@dataclass
class Page:
    path: Path
    id: str
    topic: str
    front: dict
    sections: dict[int, str] = field(default_factory=dict)

    @property
    def title(self) -> str:
        return self.front.get("title", "")


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """The YAML header as a flat dict of strings, and the rest of the page."""
    if not text.startswith("---\n"):
        return {}, text
    end = text.index("\n---", 4)
    front = {}
    for line in text[4:end].splitlines():
        key, sep, value = line.partition(":")
        if sep and re.fullmatch(r"[a-z_]+", key):
            value = value.split(" #")[0].strip()
            front[key] = value[1:-1] if len(value) >= 2 and value[0] == value[-1] == '"' else value
    return front, text[end + 4:]


def split_sections(body: str) -> dict[int, str]:
    """Section number -> its text, without the heading."""
    marks = list(SECTION_RE.finditer(body))
    out = {}
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(body)
        text = body[m.end():end]
        text = text.split("\n---\n*Part of the")[0]
        out[int(m.group(1))] = text.strip()
    return out


def bullets(text: str) -> list[str]:
    """Top-level bullets, each with its continuation lines. Empty when the section is prose."""
    starts = [m.start() for m in BULLET_RE.finditer(text)]
    items = []
    for i, start in enumerate(starts):
        end = starts[i + 1] if i + 1 < len(starts) else len(text)
        item = text[start + 2:end].strip()
        if item:
            items.append(item)
    return items


def lead_in(item: str) -> str | None:
    """The bold heading a bullet starts with ("**Numerics.** ..." -> "Numerics"), if any."""
    m = LEAD_RE.match(item)
    return m.group(1).strip().rstrip(".:") if m else None


def read_catalog(root: Path) -> list[Page]:
    pages = []
    for path in sorted((root / "topics").glob("*/*.md")):
        if path.name == "README.md":
            continue
        front, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        pages.append(Page(path=path, id=front.get("id", ""), topic=path.parent.name,
                          front=front, sections=split_sections(body)))
    return pages


def normalise_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


def parse_reference(line: str) -> dict:
    """One section-9 line -> raw tag, authors, title, venue, year, DOI, arXiv id, parse status."""
    raw = line[2:].strip() if line.startswith("- ") else line.strip()
    tag_m = TAG_RE.match(line)
    tag = tag_m.group(1).strip() if tag_m else None
    rest = line[tag_m.end():] if tag_m else raw
    doi_m = DOI_RE.search(rest)
    doi = doi_m.group(0).rstrip(".,;").lower() if doi_m else None
    arxiv_m = ARXIV_NEW_RE.search(rest) or ARXIV_OLD_RE.search(rest)
    arxiv = arxiv_m.group(1) if arxiv_m else None
    title_m = TITLE_RE.search(rest)
    title = title_m.group(1).strip().rstrip(".") if title_m else None
    authors = rest[:title_m.start()].strip().rstrip(".") if title_m else None
    after = rest[title_m.end():] if title_m else rest
    venue = re.split(r"\(|https?://", after)[0].strip(" .,") if title_m else None
    years = YEAR_RE.findall(NOT_YEAR_RE.sub(" ", after if title_m else rest))
    year = int(years[0]) if years else None
    status = "parsed" if title and year else "partial" if title else "raw"
    return {"raw_tag": tag, "raw_citation": raw, "authors": authors or None, "title": title,
            "venue": venue or None, "year": year, "doi": doi, "arxiv_id": arxiv,
            "parse_status": status}


def paper_id(ref: dict) -> str:
    """doi:<doi> when present, else a hash of the normalised title + year, else of the raw line."""
    if ref["doi"]:
        return "doi:" + ref["doi"]
    key = (f"{normalise_title(ref['title'])}|{ref['year']}" if ref["title"]
           else normalise_title(ref["raw_citation"]))
    return "paper:" + hashlib.sha1(key.encode()).hexdigest()[:16]
