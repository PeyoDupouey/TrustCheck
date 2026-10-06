# Décisions d’architecture

## D-001 — Architecture local-first

Le projet privilégie les composants open source et auto-hébergeables. Les services payants restent des fallbacks optionnels.

## D-002 — Sous-titres avant transcription

Les sous-titres accessibles d’Instagram sont utilisés avant une transcription audio, avec OCR et transcription locale comme solutions de repli.

## D-003 — Verdicts gradués

Le système ne produit pas uniquement vrai/faux. Il restitue un état, une confiance, les sources et les limites de l’analyse.

## D-004 — Prototype sans réseau par défaut

La première implémentation utilise un fournisseur de sources interchangeable et déterministe. Aucun contenu utilisateur n'est envoyé sur Internet et aucun verdict de vérité n'est simulé en l'absence de preuves.

## D-005 — Extension progressive et locale

L'extension ne bloque pas le défilement et ne lance pas une analyse sur tout le
flux. Elle propose l'analyse du post visible, affiche son état immédiatement,
annule les résultats obsolètes et appelle par défaut une API locale. Cette
limite réduit la latence, la collecte de données et la charge de calcul.
