# Phase 1 — Prototype local de vérification

## Objectif

Valider le contrat de données du moteur de vérification avant de dépendre d’Instagram, d’un LLM ou d’un moteur de recherche externe.

## Ce qui est implémenté

- extraction heuristique de phrases candidates ;
- modèle de données pour affirmations, sources et résultats ;
- fournisseur de sources interchangeable ;
- fournisseur SearXNG optionnel, sans clé API ;
- résultat prudent lorsqu’aucune preuve n’est disponible ;
- sortie JSON utilisable par une future API ou extension ;
- tests unitaires sans réseau.

## Limites connues

- l’extraction n’est pas encore faite par un LLM ;
- aucune recherche web n’est déclenchée ;
- le prototype ne conclut pas automatiquement qu’une affirmation est vraie ou fausse ;
- les sources de test sont statiques ;
- SearXNG doit être fourni par l'utilisateur et n'est pas lancé automatiquement ;
- le français est la langue cible initiale.

## Prochaine itération

Configurer une instance SearXNG locale, puis comparer ses résultats avec un petit jeu de cas annotés avant d'introduire un modèle local.

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
