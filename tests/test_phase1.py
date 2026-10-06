import unittest

from prototype.analyzer import analyze_text
from prototype.claims import extract_claims
from prototype.models import Source
from prototype.sources import StaticSourceProvider


class Phase1Tests(unittest.TestCase):
    def test_extracts_factual_sentence_and_ignores_opinion(self):
        claims = extract_claims("Cette réforme est entrée en vigueur en 2024. Je la trouve utile.")
        self.assertEqual([claim.text for claim in claims], ["Cette réforme est entrée en vigueur en 2024."])

    def test_missing_sources_is_not_presented_as_false(self):
        analysis = analyze_text("Le vaccin est dangereux.", StaticSourceProvider())
        self.assertEqual(analysis.results[0].verdict, "non vérifiable")
        self.assertEqual(analysis.results[0].confidence, 0.0)

    def test_sources_are_preserved(self):
        source = Source("Source publique", "https://example.org", "Extrait")
        analysis = analyze_text("Le taux est de 10%.", StaticSourceProvider([source]))
        self.assertEqual(analysis.results[0].sources, [source])
        self.assertEqual(analysis.results[0].verdict, "à examiner")


if __name__ == "__main__":
    unittest.main()

