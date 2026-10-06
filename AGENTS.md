# Règles de travail du projet

Ce dépôt concerne une extension de navigateur d’aide à la vérification de contenus visibles sur Instagram.

## Phase actuelle

Le projet démarre en phase de cadrage et de prototypage. Toute décision importante doit être documentée avant implémentation.

## Principes obligatoires

- Privilégier les technologies gratuites, open source et auto-hébergeables.
- Ne jamais présenter une estimation comme une vérité certaine.
- Toujours conserver les sources, leur date et le niveau de confiance associé à une analyse.
- Séparer la détection de contenu généré par IA de la vérification factuelle.
- Respecter la confidentialité, les conditions d’utilisation des plateformes et les limites légales applicables.
- Ne pas collecter de contenu privé qui n’est pas nécessaire à l’analyse demandée.
- Ne pas supprimer ou écraser des données sans validation explicite.

## Git et GitHub

- Utiliser des branches descriptives préfixées par `codex/`.
- Garder `main` stable.
- Préparer une pull request pour les changements significatifs.
- Exécuter les tests et contrôles de sécurité avant une pull request.
- Ne jamais fusionner une modification sensible sans validation humaine.
- Décrire clairement les changements, les limites et les résultats des tests.

## Méthode Codex

- Commencer par inspecter le contexte utile avant toute modification.
- Distinguer les faits vérifiés, les hypothèses et les recommandations.
- Demander confirmation avant une action externe importante ou irréversible.
- Ne pas ajouter de dépendance payante lorsqu’une solution open source raisonnable existe.
- Mettre à jour la documentation lorsqu’une décision d’architecture change.

## Documentation de référence

- `llm.txt` décrit le contrat de collaboration avec l’agent.
- `docs/PROJECT_PLAN.md` contient le plan vivant du projet.
- `docs/DECISIONS.md` contient les décisions d’architecture importantes.
