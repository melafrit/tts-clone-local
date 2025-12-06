# XTTS v2 — Interface Web locale de clonage vocal (Windows)

**Auteur : Mohamed Amine EL AFRIT**  
Site : [www.mohamedelafrit.com](https://www.mohamedelafrit.com)  
Licence : Creative Commons (recommandation académique : **CC BY 4.0 — Attribution**)

---

## Présentation

Ce projet propose une **interface web locale**, moderne et pédagogique, pour utiliser le modèle
**XTTS v2 (Coqui TTS)** afin de réaliser :

- de la **synthèse vocale multilingue**,
- et le **clonage de ta propre voix** à partir d’un fichier audio de référence.

L’objectif est d’offrir une expérience proche d’outils grand public (ergonomie, presets, réglages simples),
tout en gardant les avantages d’une exécution **100% locale sur Windows**.

---

## Points forts

- 🌐 **Interface web locale** basée sur Gradio.
- 🎙️ **Clonage vocal** via un fichier WAV de référence.
- 🧠 **XTTS v2** : modèle multilingue performant.
- 🧩 **Deux modes d’utilisation**
  - **Mode Simple** : réglages faciles (similarité, style, stabilité, vitesse).
  - **Mode Avancé** : contrôle fin des paramètres XTTS.
- 🎛️ **Presets** adaptés à des usages réels :
  - Neutre / Cours
  - Podcast naturel
  - Expressif maîtrisé
  - Très stable
- 🚀 Détection automatique **GPU/CPU**.
- ✅ Robustesse : les paramètres avancés **sont filtrés automatiquement**
  selon la version installée de `TTS` pour éviter les erreurs d’API.
- 📁 Sortie audio organisée dans `outputs/`.

---

## Démo locale

Après installation, l’interface est disponible par défaut à l’adresse :

- `http://127.0.0.1:7860`

---

## Prérequis

### Système

- Windows 10 ou 11 (64 bits)

### Python

- **Python 3.11.x recommandé**

### GPU (optionnel mais fortement conseillé)

- NVIDIA avec **8 Go de VRAM minimum**  
  **12 Go ou plus** pour un usage très confortable.

---

## Matériel recommandé

### Configuration minimale (CPU)

- CPU : 4 cœurs (8 threads recommandé)
- RAM : **16 Go**
- SSD conseillé

### Configuration conseillée (GPU)

- GPU : **NVIDIA 8–12 Go VRAM** (ou plus)
- CPU : 6–8 cœurs
- RAM : **32 Go**
- SSD

### Qualité audio d’entrée

- Micro correct (ex. Rode USB) + environnement calme
- Éviter saturation, bruit constant, forte réverbération
- **WAV propre** recommandé

---

## Arborescence proposée

```text
xtts-clone-local/
├─ xtts_web_ui_pro.py
├─ README.md
├─ FAQ.md
├─ INSTALLATION_ETUDIANTS.md
└─ docs/
   ├─ index.html
   └─ styles.css
```

---

## Installation rapide (Windows)

> Pour une version très détaillée, voir : **INSTALLATION_ETUDIANTS.md**

### 1) Créer un dossier et un venv

```powershell
mkdir C:\TTS
cd C:\TTS
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

### 2) Installer PyTorch

**GPU (CUDA 11.8)**

```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**CPU**

```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### 3) Installer les dépendances du projet

```powershell
pip install gradio
pip install TTS
```

### 4) Lancer l’interface

Place `xtts_web_ui_pro.py` dans `C:\TTS`, puis :

```powershell
python xtts_web_ui_pro.py
```

---

## Utilisation

### Étapes de base

1. Choisir la **langue de sortie**.
2. Coller le texte ou charger un **.txt**.
3. Uploader un **WAV de référence** (ou renseigner un chemin local).
4. Choisir :
   - **Mode Simple** pour démarrer rapidement,
   - **Mode Avancé** pour affiner.
5. Cliquer sur **Générer**.

Les fichiers générés sont enregistrés dans :

```text
./outputs/
```

---

## Guide de réglage rapide

### Mode Simple

- **Similarité**  
  ↑ si la voix générée s’éloigne de ton timbre.

- **Style**  
  20–35 : cours / narration pro  
  40–60 : podcast / storytelling

- **Stabilité**  
  ↑ pour des textes longs et un rendu plus constant.

- **Vitesse**  
  103–108 souvent plus naturel qu’un strict 100.

### Mode Avancé (raccourci mental)

- `gpt_cond_len` ↑ → **timbre plus fidèle**
- `temperature` ↑ → **plus vivant**, mais **moins stable**
- `noise_scale` / `noise_scale_w` ↑ → **expressivité** et **prosodie**
- `speed` / `length_scale` → **rythme global**

---

## Qualité du clonage : bonnes pratiques

- WAV propre, sans bruit parasite.
- Niveau de volume stable.
- Éviter les longues pauses et la réverbération.
- 30 secondes à 2 minutes suffisent souvent.
- Plus long peut aider sur les textes très longs.

---

## Dépannage

### L’activation du venv est bloquée

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### PyTorch ne voit pas la GPU

```powershell
python -c "import torch; print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU only')"
```

### “Aucun fichier voix valide trouvé”

- Vérifier le chemin du WAV
- Ou uploader un fichier via l’UI

---

## Sécurité et usage responsable

Le clonage vocal est une technologie puissante.

Ce projet est destiné à :
- l’expérimentation,
- l’apprentissage,
- et la production encadrée.

**Recommandations :**
- cloner **uniquement ta propre voix** ou une voix explicitement autorisée,
- éviter toute utilisation trompeuse,
- signaler l’usage d’une voix synthétique en contexte public/professionnel lorsque pertinent.

---

## FAQ

Consulte : **FAQ.md**

---

## Roadmap (idées d’amélioration)

- Découpage automatique des textes longs
- Génération en chapitres
- Export MP3 intégré
- Historique local des générations
- Presets spécialisés par langue et cas d’usage

---

## Licence

Ce projet est distribué sous la licence  
**Creative Commons Attribution 4.0 International (CC BY 4.0)**.

En bref, vous êtes autorisé à :
- **Partager** — copier et redistribuer le contenu,
- **Adapter** — remixer, transformer et développer,

**à condition de citer l’auteur** et d’indiquer les éventuelles modifications.

Le texte complet de la licence est disponible dans le fichier [`LICENSE`](./LICENSE).

**Citation recommandée :**  
> Mohamed Amine EL AFRIT, *XTTS v2 — Interface Web locale de clonage vocal (Windows)*,  
> projet disponible sur GitHub, https://www.mohamedelafrit.com,  
> sous licence CC BY 4.0.


---

## Auteur

**Mohamed Amine EL AFRIT**  
Site : [www.mohamedelafrit.com](https://www.mohamedelafrit.com)

---

## Remerciements

- Coqui TTS / XTTS v2
- PyTorch
- Gradio

![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)
