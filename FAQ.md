# FAQ — XTTS v2 Interface Web locale

Cette FAQ accompagne le projet d’interface web locale pour **XTTS v2 (Coqui TTS)**.

**Auteur : Mohamed Amine EL AFRIT**  
Site : https://www.mohamedelafrit.com

---

## 1) Général

### À quoi sert ce projet ?
Il fournit une interface web locale (Windows) pour :
- la synthèse vocale multilingue,
- le clonage de **ta propre voix** à partir d’un fichier WAV de référence,
- avec un mode simple inspiré d’outils grand public et un mode avancé pour affiner.

### Est-ce un clone d’ElevenLabs ?
Non. L’objectif est de proposer une expérience similaire côté ergonomie,
mais en s’appuyant sur un modèle **open-source** (XTTS v2) exécuté en local.

### Est-ce que tout reste en local ?
Oui, la génération se fait sur ton PC.  
Le modèle peut être téléchargé au premier usage.

---

## 2) Installation & compatibilité

### Quelle version de Python utiliser ?
**Python 3.11.x** est la recommandation principale pour éviter les conflits
de dépendances dans ce type de stack (PyTorch + TTS + Gradio).

### Pourquoi éviter Python 3.12+ ?
Certaines bibliothèques ML évoluent rapidement et ne publient pas toujours
des wheels compatibles immédiatement pour toutes les versions récentes.
Python 3.11 reste un excellent compromis stabilité/compatibilité.

### Je suis en CPU-only, est-ce utilisable ?
Oui, mais plus lent :
- parfait pour tester et comprendre,
- moins confortable pour générer de longs textes.

---

## 3) GPU

### Quelle GPU est recommandée ?
- **NVIDIA 8 Go VRAM minimum**,  
- **12 Go ou plus** idéal pour le confort.

Exemples :
- RTX 3060 12GB
- RTX 4060 Ti 16GB
- RTX 4070+

### Comment vérifier que PyTorch voit la GPU ?
```powershell
python -c "import torch; print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU only')"
