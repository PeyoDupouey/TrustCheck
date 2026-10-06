# Extension TrustCheck — prototype

Cette première extension cible Instagram Web et analyse uniquement le post
sur lequel l'utilisateur clique. Elle affiche immédiatement son état, puis
appelle l'API locale `http://127.0.0.1:8765/analyze`.

## Lancer l'API locale

Depuis la racine du dépôt :

```powershell
$env:TRUSTCHECK_SEARXNG_URL = "http://localhost:8080"
$env:TRUSTCHECK_OLLAMA_URL = "http://localhost:11434"
& "C:\Users\admin\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -m prototype.server
```

## Charger l'extension

Dans Chrome ou Edge :

1. ouvrir `chrome://extensions` ou `edge://extensions` ;
2. activer le mode développeur ;
3. choisir **Charger l’extension non empaquetée** ;
4. sélectionner le dossier `extension/` ;
5. ouvrir Instagram et cliquer sur **Analyser ce post**.

L'API reste locale. La version actuelle ne contourne pas les restrictions
d'accès d'Instagram et ne traite pas les contenus privés automatiquement.
