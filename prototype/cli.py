import argparse
import json
import os
import sys
from dataclasses import asdict

from .analyzer import analyze_text
from .llm import OllamaFactChecker
from .sources import SearxngSourceProvider, StaticSourceProvider


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Analyse locale TrustCheck")
    parser.add_argument("text", nargs="?", help="Texte à analyser")
    parser.add_argument(
        "--searxng-url",
        default=os.getenv("TRUSTCHECK_SEARXNG_URL"),
        help="URL d'une instance SearXNG compatible JSON (optionnel)",
    )
    parser.add_argument(
        "--ollama-url",
        default=os.getenv("TRUSTCHECK_OLLAMA_URL"),
        help="URL d'Ollama (optionnel, ex. http://localhost:11434)",
    )
    parser.add_argument(
        "--ollama-model",
        default=os.getenv("TRUSTCHECK_OLLAMA_MODEL", "qwen2.5:0.5b"),
        help="Modèle Ollama à utiliser",
    )
    parser.add_argument(
        "--max-claims",
        type=int,
        default=3,
        help="Nombre maximal d'affirmations du contenu visible à traiter",
    )
    args = parser.parse_args()
    text = args.text or sys.stdin.read()
    if not text.strip():
        parser.error("un texte est requis")
    provider = SearxngSourceProvider(args.searxng_url) if args.searxng_url else StaticSourceProvider()
    judge = OllamaFactChecker(args.ollama_url, args.ollama_model) if args.ollama_url else None
    print(json.dumps(asdict(analyze_text(text, provider, judge, args.max_claims)), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
