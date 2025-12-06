# Installation ultra guidée — XTTS v2 Interface Web locale (Windows)

**Auteur : Mohamed Amine EL AFRIT**  
Site : https://www.mohamedelafrit.com  
Licence : Creative Commons (recommandation académique : **CC BY 4.0 — Attribution**)

---

## 0) Objectif du guide

Ce guide te permet d’installer et de lancer **une interface web locale** pour :

- **cloner ta propre voix** à partir d’un fichier audio de référence,
- **générer de la synthèse vocale multilingue**,
- avec le modèle **XTTS v2 (Coqui TTS)**,
- directement **sur ton PC Windows**.

À la fin, tu sauras :
1. installer les prérequis,
2. créer un environnement Python propre,
3. installer PyTorch et Coqui TTS,
4. lancer l’interface web,
5. enregistrer une voix de référence de bonne qualité,
6. comprendre les réglages essentiels.

---

## 1) Pré-requis

### 1.1 Système

- Windows 10 ou 11 (64 bits)

### 1.2 Python

**Recommandé : Python 3.11.x**

Pourquoi ?
- Très bonne compatibilité avec PyTorch et Coqui TTS.
- Moins de bugs de dépendances que les versions plus récentes.

### 1.3 Matériel (important pour les performances)

#### Fonctionne en CPU (plus lent)
- RAM : 16 Go minimum
- CPU : 4 cœurs ou plus

#### Recommandé pour un usage confortable
- **GPU NVIDIA** avec 8 Go de VRAM minimum (12 Go idéal)
- RAM : 32 Go conseillés
- SSD

> Si tu n’as pas de GPU, ce n’est pas bloquant : tu pourras quand même tester et apprendre.

---

## 2) Installer Python 3.11

1) Télécharge Python 3.11 depuis le site officiel Python.  
2) Pendant l’installation :
   - ✅ coche **Add Python to PATH**
   - ✅ vérifie que l’installation inclut **pip**

3) Vérifie dans PowerShell :

```powershell
python --version
pip --version
```

Tu dois obtenir quelque chose comme :

- `Python 3.11.x`
- une version de pip

Si `python` n’est pas reconnu :
- relance l’installation de Python et coche **Add to PATH**,
- ou ferme/réouvre PowerShell.

---

## 3) Créer le dossier du projet

On va utiliser un dossier simple pour éviter les erreurs.

```powershell
mkdir C:\TTS
cd C:\TTS
```

---

## 4) Créer un environnement virtuel (obligatoire)

Un environnement virtuel isole tes dépendances et évite les conflits.

```powershell
python -m venv venv
```

Active-le :

```powershell
.\venv\Scripts\Activate.ps1
```

Tu dois voir :

```text
(venv) PS C:\TTS>
```

### Si PowerShell bloque l’activation

Tu peux autoriser l’exécution de scripts **pour ton utilisateur uniquement** :

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Puis réessaie :

```powershell
.\venv\Scripts\Activate.ps1
```

---

## 5) Mettre à jour pip

Toujours dans le venv :

```powershell
python -m pip install --upgrade pip
```

---

## 6) Installer PyTorch

### 6.1 Cas 1 — Tu as une GPU NVIDIA (recommandé)

Installe PyTorch avec CUDA 11.8 :

```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 6.2 Cas 2 — CPU uniquement

```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

---

## 7) Vérifier que PyTorch détecte la GPU (optionnel mais conseillé)

```powershell
python -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU only')"
```

---

## 8) Installer les bibliothèques du projet

Toujours dans le venv :

```powershell
pip install gradio
pip install TTS
```

---

## 9) Ajouter le script de l’interface

Place le fichier :

- `xtts_web_ui_pro.py`

dans ton dossier :

- `C:\TTS\`

Tu dois avoir :

```text
C:\TTS\
  ├─ venv\
  ├─ xtts_web_ui_pro.py
  └─ outputs\   (sera créé automatiquement si besoin)
```

---

## 10) Lancer l’interface web

Dans PowerShell :

```powershell
cd C:\TTS
.\venv\Scripts\Activate.ps1
python xtts_web_ui_pro.py
```

Le navigateur doit s’ouvrir automatiquement sur :

- http://127.0.0.1:7860

---

## 11) Enregistrer ta voix de référence (WAV)

### 11.1 Durée conseillée

- **Débutant : 30 à 60 secondes**
- **Bon niveau : 1 à 2 minutes**
- **Très bon dataset perso : 5 à 10 minutes**

> Tu peux aussi utiliser un enregistrement long si tu en as déjà un.

### 11.2 Qualité à viser

- Pièce calme
- Micro stable
- Distance constante
- Pas de souffle fort
- Pas de saturation

### 11.3 Format

- **WAV** recommandé
- Idéalement :
  - 44.1 kHz ou 48 kHz
  - mono
  - 16-bit ou 24-bit

### 11.4 Nom simple conseillé

Enregistre et nomme ton fichier :

```text
ma_voix.wav
```

Puis place-le dans :

```text
C:\TTS\
```

---

## 12) Utiliser l’interface (Mode Simple)

Le mode simple te rapproche d’une logique “grand public”.

### 12.1 Étapes

1) Choisis la **langue de sortie**.  
2) Colle ton texte (ou importe un `.txt`).  
3) Uploade ton WAV de référence.  
4) Ajuste les sliders :

### 12.2 Réglages recommandés (cours / narration pro)

- **Similarité** : 80–90  
- **Style** : 20–35  
- **Stabilité** : 50–70  
- **Vitesse** : 103–108  

5) Clique sur **Générer**.

---

## 13) Utiliser l’interface (Mode Avancé)

Tu peux démarrer par un preset :

- **Neutre / Cours**
- **Podcast naturel**
- **Expressif maîtrisé**
- **Très stable**

Ensuite, si nécessaire :

### 13.1 Signification simple des paramètres

- `gpt_cond_len`  
  → plus haut = la voix générée ressemble davantage à ta voix.

- `temperature`  
  → plus haut = plus expressif mais moins prévisible.

- `noise_scale` / `noise_scale_w`  
  → contrôle la “vie” de l’intonation.

- `speed`  
  → vitesse d’élocution.

- `length_scale`  
  → rythme global (plus posé ou plus dynamique).

---

## 14) Où sont les fichiers générés ?

Les fichiers audio générés se trouvent dans :

```text
C:\TTS\outputs\
```

---

## 15) Dépannage (très fréquent)

### 15.1 “Aucun fichier voix valide trouvé”

Solutions :
- uploade un WAV dans l’interface,
- ou vérifie ton chemin local.

### 15.2 Le navigateur ne s’ouvre pas

Ouvre manuellement :

- http://127.0.0.1:7860

### 15.3 Erreurs de dépendances

Solution robuste :

1) ferme PowerShell  
2) réouvre et relance :

```powershell
cd C:\TTS
.\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install gradio TTS
```

### 15.4 Très lent

Normal en CPU.  
Si tu peux, utilise une GPU NVIDIA.

---

## 16) Bonnes pratiques d’usage responsable

Le clonage vocal est une technologie puissante.

Tu dois :
- cloner uniquement **ta propre voix**  
  ou une voix pour laquelle tu as une autorisation claire.
- éviter les usages trompeurs.
- signaler l’usage d’une voix synthétique quand c’est pertinent.

---

## 17) Licence

Ce projet est distribué sous **licence Creative Commons**.

Dans une démarche académique et professionnelle, la recommandation par défaut est :  
**CC BY 4.0 (Attribution)**.

Cette licence autorise :
- la réutilisation,
- la distribution,
- l’adaptation,
y compris à des fins commerciales,
**à condition de citer l’auteur**.

Citation recommandée :

> Mohamed Amine EL AFRIT, *XTTS v2 — Interface Web locale de clonage vocal*,  
> projet disponible sur GitHub, www.mohamedelafrit.com.

---

## 18) Checklist rapide

Avant de demander de l’aide, vérifie :

- [ ] `python --version` → 3.11.x  
- [ ] `(venv)` visible dans PowerShell  
- [ ] `pip install gradio TTS` fait dans le venv  
- [ ] `xtts_web_ui_pro.py` bien dans `C:\TTS`  
- [ ] un vrai fichier `.wav` de référence disponible  
- [ ] lancement :

```powershell
cd C:\TTS
.\venv\Scripts\Activate.ps1
python xtts_web_ui_pro.py
```

---

## 19) Contact & ressources

**Mohamed Amine EL AFRIT**  
https://www.mohamedelafrit.com
