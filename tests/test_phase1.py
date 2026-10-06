import unittest
import json
from unittest.mock import patch

from prototype.analyzer import analyze_text
from prototype.cache import MemoryTTLCache, content_key
from prototype.claims import extract_claims
from prototype.evidence import evidence_score
from prototype.llm import OllamaFactChecker
from prototype.gemini import GeminiFactChecker
from prototype.models import Source
from prototype.sources import SearxngSourceProvider, StaticSourceProvider


class Phase1Tests(unittest.TestCase):
    def test_content_key_does_not_depend_on_whitespace_or_case(self):
        self.assertEqual(content_key("  Une   affirmation. "), content_key("une affirmation."))

    def test_ttl_cache_returns_values(self):
        cache = MemoryTTLCache(ttl_seconds=60)
        cache.put("claim", ["source"])
        self.assertEqual(cache.get("claim"), ["source"])

    def test_extracts_factual_sentence_and_ignores_opinion(self):
        claims = extract_claims("Cette réforme est entrée en vigueur en 2024. Je la trouve utile.")
        self.assertEqual([claim.text for claim in claims], ["Cette réforme est entrée en vigueur en 2024."])

    def test_prioritizes_numeric_claim_over_general_statement(self):
        claims = extract_claims(
            "Cette réforme est importante. Elle concerne 4 700 personnes en 2024."
        )
        self.assertEqual(claims[0].text, "Elle concerne 4 700 personnes en 2024.")
        self.assertGreater(claims[0].checkworthiness, claims[1].checkworthiness)

    def test_subjective_statement_is_not_selected(self):
        self.assertEqual(extract_claims("Je trouve cette réforme magnifique."), [])

    def test_missing_sources_is_not_presented_as_false(self):
        analysis = analyze_text("Le vaccin est dangereux.", StaticSourceProvider())
        self.assertEqual(analysis.results[0].verdict, "non vérifiable")
        self.assertEqual(analysis.results[0].confidence, 0.0)

    def test_sources_are_preserved(self):
        source = Source("Source publique", "https://example.org", "Extrait")
        analysis = analyze_text("Le taux est de 10%.", StaticSourceProvider([source]))
        self.assertEqual(analysis.results[0].sources, [source])
        self.assertEqual(analysis.results[0].verdict, "à examiner")
        self.assertEqual(analysis.results[0].confidence_kind, "couverture des sources")

    def test_evidence_score_ranks_matching_source_and_is_capped(self):
        claim = extract_claims("Le vaccin est administré en deux doses.")[0]
        matching = Source("Vaccin deux doses", "https://sante.gouv.fr/vaccin", "Le vaccin est administré en deux doses.")
        unrelated = Source("Sport", "https://example.org/sport", "Résultats du match.")
        score, sources = evidence_score(claim, [unrelated, matching])
        self.assertEqual(sources[0], matching)
        self.assertGreater(score, 0.4)
        self.assertLessEqual(score, 0.78)

    def test_searxng_provider_maps_json_results(self):
        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self):
                return b'{"results": [{"title": "Institution", "url": "https://example.org", "content": "Extrait"}]}'

        with patch("prototype.sources.urlopen", return_value=FakeResponse()):
            provider = SearxngSourceProvider("http://localhost:8080")
            results = provider.search(extract_claims("Le taux est de 10%.")[0])

        self.assertEqual(results[0].title, "Institution")
        self.assertEqual(results[0].url, "https://example.org")

    def test_searxng_provider_limits_results_and_caches(self):
        calls = 0

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self):
                return json.dumps({
                    "results": [
                        {"title": str(index), "url": f"https://example.org/{index}", "content": "preuve"}
                        for index in range(6)
                    ]
                }).encode("utf-8")

        def fake_urlopen(*args, **kwargs):
            nonlocal calls
            calls += 1
            return FakeResponse()

        with patch("prototype.sources.urlopen", side_effect=fake_urlopen):
            provider = SearxngSourceProvider("http://localhost:8080", max_results=2)
            claim = extract_claims("Le taux est de 10%.")[0]
            first = provider.search(claim)
            second = provider.search(claim)

        self.assertEqual(len(first), 2)
        self.assertEqual(first, second)
        self.assertEqual(calls, 1)

    def test_ollama_judge_parses_structured_response(self):
        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self):
                payload = {
                    "message": {
                        "content": '{"verdict":"confirmée","confidence":0.9,"explanation":"Les sources concordent.","source_urls":["https://example.org"]}'
                    }
                }
                return json.dumps(payload).encode("utf-8")

        source = Source("Source", "https://example.org", "Preuve")
        with patch("prototype.llm.urlopen", return_value=FakeResponse()):
            result = OllamaFactChecker().judge(extract_claims("Le taux est de 10%.")[0], [source])

        self.assertEqual(result["verdict"], "confirmée")
        self.assertEqual(result["source_urls"], ["https://example.org"])

    def test_ollama_judge_maps_short_source_indexes(self):
        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self):
                payload = {
                    "message": {
                        "content": '{"verdict":"confirmée","confidence":0.8,"explanation":"La source confirme.","source_indexes":[1]}'
                    }
                }
                return json.dumps(payload).encode("utf-8")

        sources = [
            Source("Source 1", "https://one.example", "Preuve"),
            Source("Source 2", "https://two.example", "Autre preuve"),
        ]
        with patch("prototype.llm.urlopen", return_value=FakeResponse()):
            result = OllamaFactChecker().judge(extract_claims("Le taux est de 10%.")[0], sources)

        self.assertEqual(result["source_urls"], ["https://one.example"])

    def test_gemini_judge_maps_structured_response(self):
        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self):
                payload = {
                    "candidates": [{"content": {"parts": [{"text": json.dumps({
                        "verdict": "confirmée",
                        "confidence": 0.9,
                        "explanation": "La source confirme.",
                        "source_indexes": [1],
                    })}]}}]
                }
                return json.dumps(payload).encode("utf-8")

        source = Source("Source", "https://example.org", "Preuve")
        with patch("prototype.gemini.urlopen", return_value=FakeResponse()):
            result = GeminiFactChecker("test-key").judge(extract_claims("Le taux est de 10%.")[0], [source])

        self.assertEqual(result["verdict"], "confirmée")
        self.assertEqual(result["source_urls"], ["https://example.org"])

    def test_invalid_llm_response_falls_back_to_unverifiable(self):
        class BrokenJudge:
            def judge(self, claim, sources):
                raise ValueError("JSON invalide")

        source = Source("Source", "https://example.org", "Preuve")
        analysis = analyze_text("Le taux est de 10%.", StaticSourceProvider([source]), BrokenJudge())
        self.assertEqual(analysis.results[0].verdict, "à examiner")
        self.assertGreater(analysis.results[0].confidence, 0.0)
        self.assertEqual(analysis.results[0].confidence_kind, "couverture des sources")


if __name__ == "__main__":
    unittest.main()
