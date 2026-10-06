# Phase 1 — Prototype local de vérification

## Objectif

Valider le contrat de données du moteur de vérification avant de dépendre d’Instagram, d’un LLM ou d’un moteur de recherche externe.

## Ce qui est implémenté

- extraction heuristique de phrases candidates ;
- modèle de données pour affirmations, sources et résultats ;
- fournisseur de sources interchangeable ;
- fournisseur SearXNG optionnel, sans clé API ;
- client Ollama local avec sortie JSON structurée ;
- résultat prudent lorsqu’aucune preuve n’est disponible ;
- sortie JSON utilisable par une future API ou extension ;
- cache mémoire court des recherches SearXNG ;
- limite de trois affirmations et cinq sources par contenu pour préserver la réactivité ;
- tests unitaires sans réseau.

## Limites connues

- l’extraction n’est pas encore faite par un LLM ;
- aucune recherche web n’est déclenchée ;
- le prototype ne conclut pas automatiquement qu’une affirmation est vraie ou fausse ;
- les sources de test sont statiques ;
- SearXNG doit être fourni par l'utilisateur et n'est pas lancé automatiquement ;
- le français est la langue cible initiale.
- le CLI reste synchrone : l'interface progressive et l'annulation seront ajoutées avec l'extension.

## Contrat de réactivité

Le moteur ne doit pas analyser tout le flux. L'extension cible un seul contenu
visible à la fois, affiche immédiatement un état `analyse en cours`, puis lance
la recherche et le jugement en arrière-plan. Si l'utilisateur passe au contenu
suivant, la tâche précédente doit être annulée. Les résultats sont conservés
dans un cache court indexé par empreinte, sans conserver le texte original.

## Prochaine itération

Configurer une instance SearXNG locale, puis comparer ses résultats avec un petit jeu de cas annotés avant d'introduire un modèle local.

## Analyse Ollama

Ollama est appelé uniquement lorsqu'une URL est fournie. Le modèle reçoit l'affirmation et au maximum cinq extraits de sources, puis doit retourner un verdict gradué, une confiance, une explication et les URLs utilisées. La réponse est contrainte par un schéma JSON et les URLs retournées sont filtrées contre les sources réellement fournies.

Test local :

```powershell
python -m prototype.cli --searxng-url "http://localhost:8080" --ollama-url "http://localhost:11434" "Le climat est la distribution statistique des conditions de l atmosphère terrestre."
```

## SearXNG local

Le prototype utilise une instance locale sur `http://localhost:8080`.

Configuration :

- `infra/searxng/settings.example.yml` est versionné ;
- `infra/searxng/settings.yml` reste local et est ignoré par Git ;
- le format JSON est activé pour l'appel du fournisseur TrustCheck.

Commandes Docker utiles :

```powershell
docker ps --filter name=searxng
docker start searxng
docker stop searxng
```

Test du pipeline avec recherche :

```powershell
python -m prototype.cli --searxng-url "http://localhost:8080" "Le taux est de 10%."
```
