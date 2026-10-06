import argparse
import json
import os
import sys
from dataclasses import asdict

from .analyzer import analyze_text
from .sources import SearxngSourceProvider, StaticSourceProvider


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyse locale TrustCheck")
    parser.add_argument("text", nargs="?", help="Texte à analyser")
    parser.add_argument(
        "--searxng-url",
        default=os.getenv("TRUSTCHECK_SEARXNG_URL"),
        help="URL d'une instance SearXNG compatible JSON (optionnel)",
    )
    args = parser.parse_args()
    text = args.text or sys.stdin.read()
    if not text.strip():
        parser.error("un texte est requis")
    provider = SearxngSourceProvider(args.searxng_url) if args.searxng_url else StaticSourceProvider()
    print(json.dumps(asdict(analyze_text(text, provider)), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
