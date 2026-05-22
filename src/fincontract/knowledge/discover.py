from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
import hashlib
import re
import time
from typing import Iterable
from urllib.parse import urljoin, urlparse

import httpx
import yaml


@dataclass(frozen=True)
class CrawlSource:
    id: str
    name: str
    category: str
    base_url: str
    seed_urls: list[str]
    list_page_patterns: list[str]
    doc_page_patterns: list[str]
    keywords: list[str]
    max_list_pages: int
    max_docs: int
    notes: str


@dataclass(frozen=True)
class CrawlOptions:
    sources_path: Path
    output_path: Path
    rate_limit_seconds: float
    timeout_seconds: float
    user_agent: str
    max_docs_override: int | None


class _LinkExtractor(HTMLParser):
    def __init__(self, base_url: str) -> None:
        super().__init__()
        self._base_url = base_url
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        href = None
        for key, value in attrs:
            if key.lower() == "href":
                href = value
                break
        if not href:
            return
        url = urljoin(self._base_url, href)
        self.links.append(url)


class _TitleExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._in_title = False
        self._in_h1 = False
        self._titles: list[str] = []
        self._h1: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "title":
            self._in_title = True
        if tag == "h1":
            self._in_h1 = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        if tag == "h1":
            self._in_h1 = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self._titles.append(data)
        if self._in_h1:
            self._h1.append(data)

    def extract(self) -> str:
        candidates = [" ".join(self._h1).strip(), " ".join(self._titles).strip()]
        for item in candidates:
            if item:
                return re.sub(r"\s+", " ", item)
        return ""


def _slug_from_url(url: str) -> str:
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
    return digest


def _normalize_url(url: str) -> str:
    parsed = urlparse(url)
    cleaned = parsed._replace(fragment="").geturl()
    return cleaned


def _matches_any(url: str, patterns: Iterable[str]) -> bool:
    for pattern in patterns:
        if re.search(pattern, url):
            return True
    return False


def _same_domain(url: str, base_url: str) -> bool:
    base_host = urlparse(base_url).netloc
    host = urlparse(url).netloc
    return host == base_host or host.endswith(f".{base_host}")


def _extract_date(text: str) -> str:
    match = re.search(r"(20\d{2})[年-](\d{1,2})[月-](\d{1,2})", text)
    if not match:
        return ""
    year, month, day = match.groups()
    return f"{year}-{int(month):02d}-{int(day):02d}"


def _fetch_text(client: httpx.Client, url: str) -> str:
    response = client.get(url)
    response.raise_for_status()
    return response.text


def load_sources(path: Path) -> list[CrawlSource]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    sources = []
    for item in data.get("sources", []):
        sources.append(
            CrawlSource(
                id=str(item.get("id", "")).strip(),
                name=str(item.get("name", "")).strip(),
                category=str(item.get("category", "")).strip(),
                base_url=str(item.get("base_url", "")).strip(),
                seed_urls=list(item.get("seed_urls", []) or []),
                list_page_patterns=list(item.get("list_page_patterns", []) or []),
                doc_page_patterns=list(item.get("doc_page_patterns", []) or []),
                keywords=list(item.get("keywords", []) or []),
                max_list_pages=int(item.get("max_list_pages", 10)),
                max_docs=int(item.get("max_docs", 200)),
                notes=str(item.get("notes", "")).strip(),
            )
        )
    return sources


def discover_documents(source: CrawlSource, options: CrawlOptions) -> list[dict]:
    list_queue = list(source.seed_urls)
    seen_lists: set[str] = set()
    doc_urls: set[str] = set()
    headers = {"User-Agent": options.user_agent}

    with httpx.Client(
        headers=headers,
        timeout=options.timeout_seconds,
        follow_redirects=True,
    ) as client:
        while list_queue and len(seen_lists) < source.max_list_pages:
            url = _normalize_url(list_queue.pop(0))
            if url in seen_lists:
                continue
            seen_lists.add(url)
            try:
                html = _fetch_text(client, url)
            except Exception as exc:
                print(f"[warn] list fetch failed {url} {exc}")
                continue

            extractor = _LinkExtractor(url)
            extractor.feed(html)
            for link in extractor.links:
                link = _normalize_url(link)
                if not _same_domain(link, source.base_url):
                    continue
                if _matches_any(link, source.doc_page_patterns):
                    doc_urls.add(link)
                    continue
                if source.list_page_patterns and _matches_any(link, source.list_page_patterns):
                    if link not in seen_lists:
                        list_queue.append(link)
            time.sleep(options.rate_limit_seconds)

        documents: list[dict] = []
        max_docs = options.max_docs_override or source.max_docs
        for url in sorted(doc_urls):
            if len(documents) >= max_docs:
                break
            try:
                html = _fetch_text(client, url)
                title_extractor = _TitleExtractor()
                title_extractor.feed(html)
                title = title_extractor.extract()
                if not title:
                    title = f"{source.name}-{_slug_from_url(url)}"
                if source.keywords:
                    if not any(keyword in title for keyword in source.keywords):
                        continue
                date_str = _extract_date(html) or _extract_date(title)
                documents.append(
                    {
                        "doc_id": f"{source.id}_{_slug_from_url(url)}",
                        "title": title,
                        "version": date_str,
                        "effective_date": "",
                        "source": source.base_url,
                        "url": url,
                        "format": "pdf" if url.lower().endswith(".pdf") else "html",
                        "category": source.category,
                        "enabled": True,
                    }
                )
                print(f"[ok] {source.id} {title}")
            except Exception as exc:
                print(f"[warn] doc fetch failed {url} {exc}")
            time.sleep(options.rate_limit_seconds)
        return documents


def write_documents(path: Path, documents: list[dict]) -> None:
    payload = {"version": 1, "documents": documents}
    path.write_text(yaml.safe_dump(payload, allow_unicode=True, sort_keys=False), encoding="utf-8")


def parse_args() -> CrawlOptions:
    import argparse

    parser = argparse.ArgumentParser(description="Discover knowledge documents from sources.yaml")
    parser.add_argument(
        "--sources",
        default="data/knowledge/sources.yaml",
        help="Path to sources.yaml",
    )
    parser.add_argument(
        "--output",
        default="data/knowledge/documents.yaml",
        help="Output documents.yaml",
    )
    parser.add_argument("--rate-limit", type=float, default=1.0, help="Seconds between requests")
    parser.add_argument("--timeout", type=float, default=30.0, help="HTTP timeout in seconds")
    parser.add_argument(
        "--user-agent",
        default="FinContractSentinelBot/0.1",
        help="User-Agent header for downloads",
    )
    parser.add_argument("--max-docs", type=int, default=None, help="Override max docs per source")
    args = parser.parse_args()
    return CrawlOptions(
        sources_path=Path(args.sources),
        output_path=Path(args.output),
        rate_limit_seconds=args.rate_limit,
        timeout_seconds=args.timeout,
        user_agent=args.user_agent,
        max_docs_override=args.max_docs,
    )


def main() -> int:
    options = parse_args()
    sources = load_sources(options.sources_path)
    all_documents: list[dict] = []
    for source in sources:
        if not source.seed_urls:
            continue
        print(f"[source] {source.id} seeds={len(source.seed_urls)}")
        docs = discover_documents(source, options)
        all_documents.extend(docs)
    if not all_documents:
        print("[warn] no documents discovered")
        write_documents(options.output_path, [])
        return 0
    write_documents(options.output_path, all_documents)
    print(f"[done] documents={len(all_documents)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
