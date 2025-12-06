"""
XTTS v2 - Interface Web Locale (style ElevenLabs)
=================================================

Objectif
--------
Fournir une interface web locale, esthétique et pédagogique, pour utiliser
Coqui XTTS v2 avec clonage de voix sur Windows.

Fonctionnalités
---------------
- Deux modes :
  1) Mode Simple : sliders "humains" (similarité / style / stabilité / vitesse)
     traduits automatiquement en paramètres techniques XTTS.
  2) Mode Avancé : réglage fin des paramètres (speed, temperature, etc.)
- Choix de langue de sortie.
- Choix du fichier de référence voix :
  - upload WAV via interface
  - ou chemin local vers un WAV
- Texte :
  - coller directement
  - ou charger un fichier .txt et l'importer dans la zone
- Presets préconfigurés.
- Détection automatique GPU/CPU.
- Sortie WAV dans un dossier local ./outputs

Compatibilité
-------------
- Testé conceptuellement pour Gradio 6.x.
- Le script filtre automatiquement les paramètres non supportés par
  la version installée de `TTS`, pour éviter les crashs.

Usage
-----
Depuis PowerShell (dans ton venv) :

    cd C:\\Users\\Mohamed\\TTS
    .\\venv\\Scripts\\Activate.ps1
    python xtts_web_ui_pro.py

L'interface s'ouvre automatiquement sur :
    http://127.0.0.1:7860

Notes
-----
- Usage non-commercial des modèles Coqui selon leurs conditions.
- Pour des résultats meilleurs :
  - utilise un WAV de référence propre (sans bruit, sans saturation),
    30 secondes à 2 minutes suffisent souvent.
"""

from __future__ import annotations

import os
import re
import inspect
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, List, Mapping, Union, Callable

import torch
import gradio as gr
from TTS.api import TTS as CoquiTTS


# =============================================================================
# Configuration générale (constantes)
# =============================================================================

# Accepte automatiquement les conditions d'utilisation des modèles Coqui
# afin d'éviter le prompt interactif en CLI.
os.environ["COQUI_TOS_AGREED"] = "1"

MODEL_NAME: str = "tts_models/multilingual/multi-dataset/xtts_v2"
DEFAULT_SPEAKER: str = "ma_voix_long.wav"
DEFAULT_OUT: str = "sortie_xtts.wav"

# Dossier de sortie local
OUTPUT_DIR: Path = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

# Langues proposées dans l'UI
SUPPORTED_LANGS: List[Tuple[str, str]] = [
    ("Français", "fr"),
    ("English", "en"),
    ("Español", "es"),
    ("Deutsch", "de"),
    ("Italiano", "it"),
    ("Português", "pt"),
    ("العربية", "ar"),
    ("Nederlands", "nl"),
    ("Русский", "ru"),
    ("हिन्दी", "hi"),
]

# Map label UI -> code langue XTTS
LABEL_TO_CODE: Dict[str, str] = {label: code for label, code in SUPPORTED_LANGS}


# =============================================================================
# Dataclasses
# =============================================================================

@dataclass(frozen=True)
class AdvancedParams:
    """
    Paramètres avancés XTTS.

    Ces paramètres ne sont pas garantis d'être supportés par toutes les
    versions de la librairie `TTS`. Le script filtrera en runtime ceux qui
    ne sont pas acceptés par la signature `tts.tts_to_file`.
    """
    speed: float
    temperature: float
    length_scale: float
    noise_scale: float
    noise_scale_w: float
    gpt_cond_len: int


# Presets avancés (valeurs sûres et utiles)
PRESETS_ADV: Dict[str, AdvancedParams] = {
    "Neutre / Cours": AdvancedParams(
        speed=1.02,
        temperature=0.65,
        length_scale=0.98,
        noise_scale=0.25,
        noise_scale_w=0.60,
        gpt_cond_len=1024,
    ),
    "Podcast naturel": AdvancedParams(
        speed=1.05,
        temperature=0.70,
        length_scale=0.95,
        noise_scale=0.30,
        noise_scale_w=0.70,
        gpt_cond_len=1024,
    ),
    "Expressif maîtrisé": AdvancedParams(
        speed=1.03,
        temperature=0.85,
        length_scale=0.90,
        noise_scale=0.38,
        noise_scale_w=0.85,
        gpt_cond_len=1024,
    ),
    "Très stable": AdvancedParams(
        speed=1.00,
        temperature=0.45,
        length_scale=1.00,
        noise_scale=0.18,
        noise_scale_w=0.50,
        gpt_cond_len=768,
    ),
}


# =============================================================================
# Détection device + chargement modèle
# =============================================================================

DEVICE: str = "cuda" if torch.cuda.is_available() else "cpu"

# Instance globale du moteur TTS pour éviter de recharger le modèle à chaque clic.
tts: CoquiTTS

try:
    # Tentative moderne : instanciation sans paramètre gpu, puis .to(device)
    tts = CoquiTTS(model_name=MODEL_NAME, progress_bar=False)
    if hasattr(tts, "to"):
        try:
            tts.to(DEVICE)
        except Exception:
            # Si la méthode existe mais échoue, on laisse l'objet tel quel.
            pass
except TypeError:
    # Fallback ancien style (paramètre gpu au constructeur)
    tts = CoquiTTS(model_name=MODEL_NAME, progress_bar=False, gpu=(DEVICE == "cuda"))


# =============================================================================
# Helpers fichiers et sécurité Windows
# =============================================================================

def sanitize_filename(name: str) -> str:
    """
    Normalise un nom de fichier pour Windows et garantit une extension .wav.

    Parameters
    ----------
    name:
        Nom de fichier saisi par l'utilisateur.

    Returns
    -------
    str
        Nom de fichier sécurisé et terminé par .wav.
    """
    cleaned: str = (name or "").strip()
    if not cleaned:
        cleaned = DEFAULT_OUT

    # Remplace les caractères non autorisés par underscore.
    cleaned = re.sub(r'[<>:"/\\|?*]', "_", cleaned)

    # Force l'extension wav.
    if not cleaned.lower().endswith(".wav"):
        cleaned += ".wav"

    return cleaned


def filter_kwargs(func: Callable[..., Any], kwargs: Mapping[str, Any]) -> Dict[str, Any]:
    """
    Filtre `kwargs` pour ne garder que les paramètres acceptés par `func`.

    Cela rend le script robuste face aux variations de l'API `TTS` selon
    les versions installées.

    Parameters
    ----------
    func:
        Fonction cible (ex: tts.tts_to_file).
    kwargs:
        Dictionnaire de paramètres proposés.

    Returns
    -------
    Dict[str, Any]
        Paramètres compatibles avec la signature de la fonction.
    """
    try:
        sig = inspect.signature(func)
        allowed = set(sig.parameters.keys())
        return {k: v for k, v in kwargs.items() if k in allowed and v is not None}
    except Exception:
        # Si l'introspection échoue, on renvoie un dict vide pour éviter un crash.
        return {}


def extract_path(file_obj: Any) -> Optional[str]:
    """
    Extrait un chemin local depuis une valeur de fichier Gradio.

    Gradio peut fournir :
    - une string path
    - un objet avec attribut `.name`
    - un dict contenant `path` ou `name`

    Parameters
    ----------
    file_obj:
        Objet fourni par Gradio.

    Returns
    -------
    Optional[str]
        Chemin local si détecté, sinon None.
    """
    if file_obj is None:
        return None

    # Cas direct : string
    if isinstance(file_obj, str):
        return file_obj

    # Cas objet avec attribut .name
    if hasattr(file_obj, "name") and isinstance(getattr(file_obj, "name"), str):
        return getattr(file_obj, "name")

    # Cas dict
    if isinstance(file_obj, dict):
        if "path" in file_obj and isinstance(file_obj["path"], str):
            return file_obj["path"]
        if "name" in file_obj and isinstance(file_obj["name"], str):
            return file_obj["name"]

    return None


def resolve_speaker_path(speaker_upload: Any, path_text: str) -> str:
    """
    Détermine le fichier WAV de référence utilisé pour le clonage.

    Priorité :
    1) WAV uploadé via l'UI
    2) chemin local saisi dans la textbox
    3) DEFAULT_SPEAKER si présent
    sinon erreur.

    Parameters
    ----------
    speaker_upload:
        Fichier uploadé par Gradio.
    path_text:
        Chemin local saisi par l'utilisateur.

    Returns
    -------
    str
        Chemin valide vers un WAV de référence.

    Raises
    ------
    FileNotFoundError
        Si aucun fichier valide n'est trouvé.
    """
    uploaded_path: Optional[str] = extract_path(speaker_upload)
    if uploaded_path and os.path.exists(uploaded_path):
        return uploaded_path

    manual_path: str = (path_text or "").strip()
    if manual_path and os.path.exists(manual_path):
        return manual_path

    if os.path.exists(DEFAULT_SPEAKER):
        return DEFAULT_SPEAKER

    raise FileNotFoundError(
        "Aucun fichier voix valide trouvé. "
        "Uploade un WAV ou renseigne un chemin existant."
    )


def load_text_from_file(txt_file: Any) -> str:
    """
    Charge un contenu texte depuis un fichier .txt uploadé.

    Parameters
    ----------
    txt_file:
        Objet fichier Gradio.

    Returns
    -------
    str
        Contenu du fichier ou chaîne vide si indisponible.
    """
    path: Optional[str] = extract_path(txt_file)
    if not path or not os.path.exists(path):
        return ""

    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# =============================================================================
# Mapping "Simple" -> "Avancé"
# =============================================================================

def clamp(value: float, low: float, high: float) -> float:
    """
    Limite une valeur dans une plage.

    Parameters
    ----------
    value:
        Valeur à borner.
    low:
        Borne basse.
    high:
        Borne haute.

    Returns
    -------
    float
        Valeur bornée.
    """
    return max(low, min(high, value))


def map_simple_to_adv(
    similarity: float,
    style: float,
    stability: float,
    speed_pct: float
) -> AdvancedParams:
    """
    Convertit des sliders "humains" en paramètres XTTS techniques.

    Cette fonction crée un comportement proche d'ElevenLabs pour aider
    un utilisateur non spécialiste à obtenir rapidement un bon résultat.

    Interprétation
    --------------
    - similarity (0..100) :
        augmente la fidélité au timbre via gpt_cond_len
    - style (0..100) :
        augmente l'expressivité via temperature/noise*
    - stability (0..100) :
        stabilise la voix (réduit variabilité)
    - speed_pct (80..120) :
        vitesse de lecture en pourcentage

    Parameters
    ----------
    similarity:
        0 à 100.
    style:
        0 à 100.
    stability:
        0 à 100.
    speed_pct:
        80 à 120.

    Returns
    -------
    AdvancedParams
        Paramètres avancés calculés.
    """
    # Vitesse : mapping direct autour de 1.0
    speed: float = clamp(speed_pct / 100.0, 0.85, 1.25)

    # Similarité : plage pratique 256..1536 (arrondie par pas de 64)
    gpt_raw: float = 256.0 + (similarity / 100.0) * (1536.0 - 256.0)
    gpt_cond_len: int = int(round(gpt_raw / 64.0) * 64)

    # Expressivité :
    # base_temp augmente avec style
    base_temp: float = 0.55 + (style / 100.0) * 0.45  # 0.55..1.00

    # La stabilité contrebalance la variabilité
    stab_factor: float = 1.0 - (stability / 100.0) * 0.45
    temperature: float = clamp(base_temp * stab_factor, 0.35, 1.05)

    # noise_scale : variation locale
    base_noise: float = 0.22 + (style / 100.0) * 0.20  # 0.22..0.42
    noise_scale: float = clamp(
        base_noise * (0.85 + (1.0 - stability / 100.0) * 0.30),
        0.15, 0.50
    )

    # noise_scale_w : prosodie globale
    base_noise_w: float = 0.55 + (style / 100.0) * 0.35  # 0.55..0.90
    noise_scale_w: float = clamp(
        base_noise_w * (0.90 + (1.0 - stability / 100.0) * 0.20),
        0.40, 0.95
    )

    # length_scale : rythme global (plus bas = plus dynamique)
    length_scale: float = clamp(
        1.00 - (style / 100.0) * 0.12,
        0.88, 1.05
    )

    return AdvancedParams(
        speed=speed,
        temperature=temperature,
        length_scale=length_scale,
        noise_scale=noise_scale,
        noise_scale_w=noise_scale_w,
        gpt_cond_len=gpt_cond_len,
    )


# =============================================================================
# Moteurs de synthèse
# =============================================================================

def synthesize_advanced(
    text: str,
    lang_label: str,
    out_name: str,
    speaker_upload: Any,
    speaker_path_text: str,
    preset_name: str,
    speed: float,
    temperature: float,
    length_scale: float,
    noise_scale: float,
    noise_scale_w: float,
    gpt_cond_len: int,
) -> Tuple[Optional[str], str]:
    """
    Réalise une synthèse vocale en appliquant des paramètres avancés XTTS.

    Cette fonction :
    1) valide le texte,
    2) résout le fichier de référence voix,
    3) applique éventuellement un preset,
    4) filtre les kwargs non supportés par l'API,
    5) génère le fichier WAV dans OUTPUT_DIR.

    Parameters
    ----------
    text:
        Texte à synthétiser.
    lang_label:
        Libellé de langue choisi dans l'UI.
    out_name:
        Nom du fichier de sortie.
    speaker_upload:
        Fichier WAV uploadé.
    speaker_path_text:
        Chemin local d'un WAV.
    preset_name:
        Nom du preset avancé sélectionné.
    speed, temperature, length_scale, noise_scale, noise_scale_w, gpt_cond_len:
        Paramètres avancés XTTS.

    Returns
    -------
    Tuple[Optional[str], str]
        - chemin du fichier WAV généré (ou None)
        - message de log utilisateur
    """
    cleaned_text: str = (text or "").strip()
    if len(cleaned_text) < 5:
        return None, "❌ Texte trop court."

    lang_code: str = LABEL_TO_CODE.get(lang_label, "fr")
    out_file: str = sanitize_filename(out_name)
    out_path: Path = OUTPUT_DIR / out_file

    try:
        speaker_wav: str = resolve_speaker_path(speaker_upload, speaker_path_text)
    except Exception as e:
        return None, f"❌ Problème fichier voix : {e}"

    # Si un preset est choisi, il override les valeurs manuelles.
    if preset_name in PRESETS_ADV:
        preset: AdvancedParams = PRESETS_ADV[preset_name]
        speed = preset.speed
        temperature = preset.temperature
        length_scale = preset.length_scale
        noise_scale = preset.noise_scale
        noise_scale_w = preset.noise_scale_w
        gpt_cond_len = preset.gpt_cond_len

    # Paramètres proposés à l'API
    proposed: Dict[str, Any] = {
        "speed": float(speed),
        "temperature": float(temperature),
        "length_scale": float(length_scale),
        "noise_scale": float(noise_scale),
        "noise_scale_w": float(noise_scale_w),
        "gpt_cond_len": int(gpt_cond_len),
    }

    # On ne garde que les paramètres acceptés par tts_to_file
    extra: Dict[str, Any] = filter_kwargs(tts.tts_to_file, proposed)

    # Appel principal avec fallback sécurisé
    try:
        tts.tts_to_file(
            text=cleaned_text,
            speaker_wav=speaker_wav,
            language=lang_code,
            file_path=str(out_path),
            **extra,
        )
    except TypeError:
        # Si l'API refuse les kwargs pour une raison de compat,
        # on retente sans params avancés.
        tts.tts_to_file(
            text=cleaned_text,
            speaker_wav=speaker_wav,
            language=lang_code,
            file_path=str(out_path),
        )
    except Exception as e:
        return None, f"❌ Erreur synthèse : {e}"

    applied: str = ", ".join(extra.keys()) if extra else "paramètres avancés non appliqués (API limitée)"
    msg: str = (
        f"✅ Audio généré : {out_path}\n"
        f"🖥️ Device : {DEVICE}\n"
        f"🌍 Langue : {lang_code}\n"
        f"🎙️ Référence : {speaker_wav}\n"
        f"🧪 Paramètres appliqués : {applied}"
    )

    return str(out_path), msg


def synthesize_simple(
    text: str,
    lang_label: str,
    out_name: str,
    speaker_upload: Any,
    speaker_path_text: str,
    similarity: float,
    style: float,
    stability: float,
    speed_pct: float,
) -> Tuple[Optional[str], str]:
    """
    Synthèse en mode simple (style ElevenLabs).

    Transforme les 4 sliders utilisateurs en paramètres avancés via
    `map_simple_to_adv`, puis appelle `synthesize_advanced`.

    Parameters
    ----------
    text:
        Texte à synthétiser.
    lang_label:
        Libellé de langue choisi dans l'UI.
    out_name:
        Nom du fichier de sortie.
    speaker_upload:
        WAV uploadé.
    speaker_path_text:
        Chemin local vers un WAV.
    similarity:
        0..100 — fidélité au timbre.
    style:
        0..100 — expressivité.
    stability:
        0..100 — stabilité.
    speed_pct:
        80..120 — vitesse.

    Returns
    -------
    Tuple[Optional[str], str]
        Chemin audio et log.
    """
    mapped: AdvancedParams = map_simple_to_adv(similarity, style, stability, speed_pct)

    return synthesize_advanced(
        text=text,
        lang_label=lang_label,
        out_name=out_name,
        speaker_upload=speaker_upload,
        speaker_path_text=speaker_path_text,
        preset_name="",  # no preset in simple mode
        speed=mapped.speed,
        temperature=mapped.temperature,
        length_scale=mapped.length_scale,
        noise_scale=mapped.noise_scale,
        noise_scale_w=mapped.noise_scale_w,
        gpt_cond_len=mapped.gpt_cond_len,
    )


# =============================================================================
# UI Gradio (mise en forme)
# =============================================================================

CSS: str = """
:root { --radius: 14px; }

.gradio-container {
  font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
}

.app-hero {
  border: 1px solid rgba(0,0,0,0.06);
  background: linear-gradient(120deg, rgba(0,0,0,0.03), rgba(0,0,0,0.00));
  padding: 18px 20px;
  border-radius: var(--radius);
}

.section-card {
  border: 1px solid rgba(0,0,0,0.06);
  border-radius: var(--radius);
  padding: 14px 14px 6px 14px;
  background: rgba(255,255,255,0.6);
}

.small-muted { opacity: 0.75; font-size: 0.92em; }
"""


# =============================================================================
# Construction de l'application Gradio
# =============================================================================

def build_app() -> gr.Blocks:
    """
    Construit et retourne l'application Gradio.

    Les composants sont organisés en sections logiques et en deux onglets :
    - Mode Simple
    - Mode Avancé

    Returns
    -------
    gr.Blocks
        Application prête à être lancée.
    """
    with gr.Blocks(title="XTTS v2 — Clone vocal local (Pro)") as demo:
        # Header visuel
        gr.Markdown(
            """
<div class="app-hero">
  <h1>XTTS v2 — Clone vocal local</h1>
  <p class="small-muted">
    Interface locale inspirée d’ElevenLabs : un mode Simple pour démarrer,
    et un mode Avancé pour affiner la voix. Tout se fait en local sur ton PC.
  </p>
</div>
"""
        )

        # Infos système
        with gr.Row():
            device_box: gr.Textbox = gr.Textbox(
                label="Device détecté",
                value=DEVICE,
                interactive=False
            )
            model_box: gr.Textbox = gr.Textbox(
                label="Modèle",
                value=MODEL_NAME,
                interactive=False
            )
            out_dir_box: gr.Textbox = gr.Textbox(
                label="Dossier de sortie",
                value=str(OUTPUT_DIR.resolve()),
                interactive=False
            )

        # Section texte + voix
        with gr.Row():
            # --- Texte ---
            with gr.Column(scale=6):
                gr.Markdown("### Texte à lire")
                text_file: gr.File = gr.File(
                    label="Charger un fichier texte (.txt) — optionnel",
                    file_types=[".txt"]
                )
                text_input: gr.Textbox = gr.Textbox(
                    label="Ou coller le texte ici",
                    lines=10,
                    placeholder="Colle ton texte ici…"
                )
                load_btn: gr.Button = gr.Button("Importer le .txt dans la zone de texte")

            # --- Voix de référence ---
            with gr.Column(scale=4):
                gr.Markdown("### Voix de référence")
                speaker_upload: gr.File = gr.File(
                    label="Uploader ta voix (WAV)",
                    file_types=[".wav"]
                )
                speaker_path_text: gr.Textbox = gr.Textbox(
                    label="Ou chemin local vers un WAV",
                    value=DEFAULT_SPEAKER,
                    info=(
                        "Si tu ne veux pas uploader, "
                        "indique ici le chemin d'un fichier WAV existant."
                    )
                )
                gr.Markdown(
                    "<p class='small-muted'>"
                    "Conseil : un WAV propre de 30s à 2min suffit généralement. "
                    "Un enregistrement long peut améliorer la cohérence sur des textes longs."
                    "</p>"
                )

        # Bouton d'import .txt -> textbox
        load_btn.click(fn=load_text_from_file, inputs=[text_file], outputs=[text_input])

        # Langue + fichier de sortie
        with gr.Row():
            lang_dropdown: gr.Dropdown = gr.Dropdown(
                label="Langue de sortie",
                choices=[label for label, _ in SUPPORTED_LANGS],
                value="Français",
                info="Choisis la langue dans laquelle le texte sera prononcé."
            )
            out_name: gr.Textbox = gr.Textbox(
                label="Nom du fichier de sortie",
                value=DEFAULT_OUT,
                info="L’extension .wav sera ajoutée si elle manque."
            )

        gr.Markdown("---")

        # Résultats
        audio_out: gr.Audio
        log_out: gr.Textbox

        # Onglets mode Simple / Avancé
        with gr.Tabs():
            # =================================================================
            # MODE SIMPLE
            # =================================================================
            with gr.Tab("Mode Simple (recommandé)"):
                gr.Markdown(
                    """
<div class="section-card">
  <b>Mode Simple</b> : des réglages compréhensibles pour tous.
  <br>Idéal pour obtenir rapidement un résultat proche d’ElevenLabs.
</div>
"""
                )

                with gr.Row():
                    similarity: gr.Slider = gr.Slider(
                        0, 100, value=85, step=1,
                        label="Fidélité à ta voix (Similarité)",
                        info=(
                            "Plus haut = le timbre colle davantage à ta voix. "
                            "Si la voix dérive ou te ressemble moins, augmente. "
                            "Si le rendu devient trop rigide, baisse un peu."
                        )
                    )
                    style: gr.Slider = gr.Slider(
                        0, 100, value=30, step=1,
                        label="Expressivité (Style)",
                        info=(
                            "Plus haut = intonation plus vivante. "
                            "Cours/narration pro : 20–35. "
                            "Podcast plus dynamique : 40–60."
                        )
                    )

                with gr.Row():
                    stability: gr.Slider = gr.Slider(
                        0, 100, value=55, step=1,
                        label="Stabilité",
                        info=(
                            "Plus haut = voix plus régulière, moins de variations. "
                            "Utile pour textes longs. "
                            "Si la voix devient monotone, baisse un peu."
                        )
                    )
                    speed_pct: gr.Slider = gr.Slider(
                        80, 120, value=105, step=1,
                        label="Vitesse",
                        info=(
                            "100 = normal. "
                            "Souvent, 103–108 donne un rendu plus naturel."
                        )
                    )

                gen_simple: gr.Button = gr.Button("Générer (mode simple)")

            # =================================================================
            # MODE AVANCÉ
            # =================================================================
            with gr.Tab("Mode Avancé (fine-tuning)"):
                gr.Markdown(
                    """
<div class="section-card">
  <b>Mode Avancé</b> : contrôle fin des paramètres XTTS.
  <br>Si un paramètre n’est pas supporté par ta version de TTS,
  il sera ignoré automatiquement.
</div>
"""
                )

                preset_dropdown: gr.Dropdown = gr.Dropdown(
                    label="Preset",
                    choices=list(PRESETS_ADV.keys()),
                    value="Neutre / Cours",
                    info="Commence par un preset puis ajuste si nécessaire."
                )

                with gr.Accordion("Paramètres avancés", open=True):
                    speed: gr.Slider = gr.Slider(
                        0.8, 1.25, value=1.05, step=0.01,
                        label="speed (vitesse d’élocution)",
                        info=(
                            "1.00 = neutre. "
                            "1.03–1.08 est souvent plus naturel. "
                            "Si la diction devient trop rapide, baisse."
                        )
                    )
                    temperature: gr.Slider = gr.Slider(
                        0.1, 1.2, value=0.65, step=0.01,
                        label="temperature (variabilité/stabilité)",
                        info=(
                            "Plus bas = plus stable. "
                            "Plus haut = plus vivant mais parfois moins régulier. "
                            "Cours/texte long : 0.55–0.75."
                        )
                    )
                    length_scale: gr.Slider = gr.Slider(
                        0.85, 1.15, value=0.95, step=0.01,
                        label="length_scale (rythme global)",
                        info=(
                            "Plus bas = rythme plus dynamique. "
                            "Plus haut = plus posé."
                        )
                    )
                    noise_scale: gr.Slider = gr.Slider(
                        0.1, 0.6, value=0.30, step=0.01,
                        label="noise_scale (expressivité locale)",
                        info=(
                            "Contrôle la variation locale d’intonation. "
                            "0.25–0.38 est une plage sûre. "
                            "Si le rendu devient trop théâtral, baisse."
                        )
                    )
                    noise_scale_w: gr.Slider = gr.Slider(
                        0.1, 1.0, value=0.70, step=0.01,
                        label="noise_scale_w (prosodie globale)",
                        info=(
                            "Ajuste la musicalité globale. "
                            "Si l’intonation est trop plate, augmente légèrement."
                        )
                    )
                    gpt_cond_len: gr.Slider = gr.Slider(
                        256, 2048, value=1024, step=64,
                        label="gpt_cond_len (poids de la voix de référence)",
                        info=(
                            "Plus haut = plus fidèle à ton timbre. "
                            "Si tu sens une dérive du timbre, augmente. "
                            "Si la voix devient trop rigide, baisse un peu."
                        )
                    )

                gen_adv: gr.Button = gr.Button("Générer (mode avancé)")

        # Sorties communes aux deux modes
        gr.Markdown("---")
        with gr.Row():
            audio_out = gr.Audio(label="Résultat", type="filepath")
            log_out = gr.Textbox(label="Journal", lines=8)

        # Wiring des callbacks
        gen_simple.click(
            fn=synthesize_simple,
            inputs=[
                text_input, lang_dropdown, out_name,
                speaker_upload, speaker_path_text,
                similarity, style, stability, speed_pct
            ],
            outputs=[audio_out, log_out]
        )

        gen_adv.click(
            fn=synthesize_advanced,
            inputs=[
                text_input, lang_dropdown, out_name,
                speaker_upload, speaker_path_text,
                preset_dropdown,
                speed, temperature, length_scale, noise_scale, noise_scale_w, gpt_cond_len
            ],
            outputs=[audio_out, log_out]
        )

    return demo


# =============================================================================
# Point d'entrée
# =============================================================================

def main() -> None:
    """
    Point d'entrée principal.

    Construit l'application Gradio et la lance en local.

    En Gradio 6.x, `css` et `theme` doivent être fournis à `launch()`
    et non à `gr.Blocks(...)`.
    """
    demo: gr.Blocks = build_app()

    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        inbrowser=True,
        theme=gr.themes.Soft(),
        css=CSS,
    )


if __name__ == "__main__":
    main()
