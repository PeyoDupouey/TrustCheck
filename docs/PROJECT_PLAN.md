# Plan du projet

## Objectif

Créer une extension de navigateur qui analyse le contenu visible sur Instagram et présente une vérification sourcée des affirmations détectées.

## MVP

- Instagram Web uniquement.
- Analyse déclenchée par l’utilisateur ou lors de l'arrivée d'un post visible.
- Retour visuel immédiat (`analyse en cours`) puis résultat progressif.
- Texte visible et sous-titres accessibles en priorité.
- OCR en complément pour le texte incrusté.
- Extraction des affirmations vérifiables.
- Recherche de sources publiques.
- Cache court par contenu et analyse limitée au post visible.
- Verdict nuancé avec confiance, explication et citations.

## Hors périmètre initial

- Analyse continue de tout le flux.
- Garantie de vérité absolue.
- Analyse de comptes privés.
- Détection définitive de contenu généré par IA.
- Application mobile native.

## Architecture cible

- Extension : TypeScript et WebExtensions.
- Backend : Python et FastAPI.
- Données : PostgreSQL, avec Redis ou Valkey si une file de tâches est nécessaire.
- OCR : PaddleOCR ou Tesseract.
- Transcription de secours : Whisper ou faster-whisper.
- LLM local prioritaire : Ollama avec un modèle compatible.
- Déploiement local : Docker Compose.
- CI : GitHub Actions.

## Étapes

1. Valider le périmètre et le nom du dépôt.
2. Initialiser le dépôt et la documentation.
3. Concevoir le contrat d’analyse et le format des preuves.
4. Prototyper l’extraction d’affirmations hors navigateur. **En cours — voir `docs/PHASE_1.md`.**
5. Ajouter l’extension minimale avec annulation, cache et analyse progressive.
6. Ajouter les sous-titres, l’OCR et la transcription fallback.
7. Construire le jeu d’évaluation et mesurer les erreurs.
8. Préparer une bêta limitée.

## Critères de réussite du MVP

- Chaque verdict affiche ses sources.
- Les contenus non vérifiables sont explicitement signalés.
- Les résultats peuvent être reproduits à partir des entrées et des sources conservées.
- L’analyse fonctionne sans fournisseur payant obligatoire en environnement local.
- Les tests couvrent les cas vrais, faux, ambigus et satiriques.
