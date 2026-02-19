# Diagnostic : le backend ne reçoit rien

## Ce qu’on sait

- Le **navigateur** envoie une requête vers `http://127.0.0.1:8011/upload` et reçoit une **réponse 500**.
- Donc **quelque chose** écoute sur le port **8011** et renvoie cette 500.
- Si **aucune ligne** n’apparaît dans le terminal où tu as lancé uvicorn, alors soit :
  1. Ce n’est **pas** ce processus qui écoute sur 8011 (un autre le fait),  
  2. Soit la 500 est renvoyée **avant** d’atteindre ton app (ex. uvicorn, proxy, autre outil).

## Étapes de diagnostic (sans tout casser)

### 1. Qui écoute sur 8011 ?

Dans **PowerShell** ou **cmd** :

```bash
netstat -ano | findstr :8011
```

Tu dois voir une ligne avec `LISTENING` et un **PID** (dernier nombre).

- Si tu ne vois **rien** : aucun processus n’écoute sur 8011 → le front appelle peut‑être un mauvais port ou une ancienne config (rafraîchir la page, vérifier `src/config.ts`).
- Si tu vois un PID : note-le (ex. `12345`).

### 2. C’est bien ton backend ?

Au démarrage, le backend affiche maintenant :

```text
[BACKEND] Démarré — PID=XXXXX (ce processus). ...
```

- Compare ce **PID** avec celui donné par `netstat -ano | findstr :8011`.
- Si ce n’est **pas le même** → un **autre** processus (ancien uvicorn, autre script) tient le port 8011. Ton vrai backend tourne ailleurs (ou pas sur 8011). Il faut arrêter l’autre processus ou changer de port.

### 3. Un seul backend, bon port

- Arrête **tous** les uvicorn (fermer les terminaux ou Ctrl+C).
- Depuis la racine du projet, lance **une seule fois** :
  ```bash
  uvicorn backend.main:app --reload --port 8011
  ```
- Vérifie que le PID affiché au démarrage est le **même** que celui de `netstat -ano | findstr :8011`.
- Réessaie l’upload depuis le front : tu devrais voir au moins :
  ```text
  [BACKEND] Requête reçue: POST /upload
  ```
  Si cette ligne apparaît, le backend reçoit bien la requête ; la 500 vient du code (upload, ollama, etc.). Si elle n’apparaît pas alors que netstat montre bien le bon PID, la requête est traitée ailleurs (proxy, autre instance).

### 4. Test direct (sans le front)

Pour être sûr que c’est bien ton app qui répond sur 8011 :

```bash
curl -v -X POST http://127.0.0.1:8011/upload -F "file=@C:\chemin\vers\un.pdf"
```

(remplace par un vrai chemin vers un PDF.)

- Si dans le **même** terminal que uvicorn tu vois `[BACKEND] Requête reçue: POST /upload` (et éventuellement une erreur après), alors le backend reçoit bien les requêtes ; le souci peut être le navigateur (cache, ancienne URL) ou un autre processus qui répondait avant.
- Si curl reçoit une 500 mais **aucune** ligne dans le terminal du backend → ce n’est pas ce processus qui répond sur 8011.

## En résumé

- **Rien dans le terminal** alors que le navigateur a une 500 = très souvent **un autre processus** sur 8011, ou tu regardes le mauvais terminal.
- Utilise **PID + netstat** pour vérifier que c’est bien **ton** uvicorn qui écoute sur 8011, et **un seul** backend lancé avec `--port 8011`.
