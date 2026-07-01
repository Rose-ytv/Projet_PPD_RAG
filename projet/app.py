"""
Serveur Flask -- interface web du systeme RAG.
CORRECTION : utilise desormais RagPipeline (plus de duplication),
et affiche les sources avec page/section dans la reponse JSON
(le projet original ne renvoyait que le texte brut des chunks, sans
metadonnees -- impossible donc d'afficher une citation correcte).
"""
import warnings
import os
import logging

warnings.filterwarnings("ignore")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)

from flask import Flask, render_template, request, jsonify
from src.rag.pipeline import RagPipeline
from src.rag.config import cfg

app = Flask(__name__)

# Pipeline charge une seule fois au demarrage du serveur
_pipeline = RagPipeline()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/question", methods=["POST"])
def question():
    data = request.get_json() or {}
    q = data.get("question", "").strip()

    if not q:
        return jsonify({"erreur": "Veuillez entrer une question."})
    if len(q) < 10:
        return jsonify({"erreur": "Votre question est trop courte. Veuillez la reformuler."})

    reponse, chunks = _pipeline.ask(q)

    sources = [
        {
            "source": c.source,
            "section": c.section,
            "page": c.page,
            "extrait": c.text[:200] + "..." if len(c.text) > 200 else c.text,
        }
        for c in chunks
    ]

    return jsonify({"reponse": reponse, "chunks": [c.text for c in chunks], "sources": sources})


@app.route("/sante")
def sante():
    try:
        total = _pipeline.count()
        return jsonify({"statut": "ok", "chunks_indexes": total})
    except Exception as e:
        return jsonify({"statut": "erreur", "detail": str(e)}), 500


if __name__ == "__main__":
    app.run(host=cfg.app.host, port=cfg.app.port, debug=cfg.app.debug)
