"""
Chargement de la configuration depuis config.yaml.
Un seul endroit pour lire la config -- tous les modules importent d'ici.
Corrige la duplication du projet original ou "all-MiniLM-L6-v2" et
"http://localhost:6333" etaient repetes dans 4 fichiers differents.
"""
import os
from pathlib import Path
import yaml
from dotenv import load_dotenv

load_dotenv()

_ROOT = Path(__file__).parent.parent.parent
_config_path = _ROOT / "config.yaml"

with open(_config_path) as f:
    _cfg = yaml.safe_load(f)


class _Section:
    def __init__(self, d: dict):
        for k, v in d.items():
            setattr(self, k, _Section(v) if isinstance(v, dict) else v)


cfg = _Section(_cfg)

# Variable d'environnement (secret) -- jamais en clair dans le code
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
