import argparse
import json
import sys
from dataclasses import asdict

from .analyzer import analyze_text
from .sources import StaticSourceProvider


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyse locale TrustCheck")
    parser.add_argument("text", nargs="?", help="Texte à analyser")
    args = parser.parse_args()
    text = args.text or sys.stdin.read()
    if not text.strip():
        parser.error("un texte est requis")
    print(json.dumps(asdict(analyze_text(text, StaticSourceProvider())), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

