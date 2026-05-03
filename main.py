"""
Auteurs: Nathan
Permet de lancer le serveur et de gérer la connection entre les programmes python et le frontend
"""

from flask import Flask, render_template, request, Response, jsonify
from flask import Blueprint, abort
import os
import time
import json

from graph import Graphe, get_regions_france
from utils import display_graph, progress_data
from color import *

app = Flask(__name__)

# Permet l'accès au dossier `imgs` depuis le site web
imgs = Blueprint("imgs", __name__, static_url_path="/imgs", static_folder="saves/imgs")
app.register_blueprint(imgs)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/maps") # Vide
def maps():
    return render_template("maps.html")

@app.route("/maps/<id>")
def map(id):
    """
    Page d'affichage de la carte

    Parameters
    ----------
    id: str
        résultat sha1 de l'image
    """
    path = f"saves/{id}.json"

    if not os.path.isfile(path): # Aucune sauvegarde trouvée
        abort(404)

    with open(path) as f:
        centers = json.load(f)["centers"] # Récupérer centres des régions
    return render_template("map.html", id=id, centers=centers)

@app.route("/upload")
def upload():
    """Page web d'upload d'une img"""
    return render_template("upload.html")

@app.route("/upload-map", methods=["POST"])
def upload_map():
    """Route transmettant le fichier image donnée par l'utilisateur"""
    # Réception du fichier
    file = request.files["file"]
    path = "assets/temp"
    i = 0

    while os.path.isfile(path + str(i) + ".png"): # Choix d'un nom non utilisé
        i += 1
    path = path + str(i) + ".png"

    file.save(path) # Stockage fichier pour traitement

    result = Graphe.from_map_image(path)

    os.remove(path) # Supprimer image origine après traitement

    return jsonify({
        "status": "success",
        "data": result.map_id
    })

@app.route("/progress")
def progress():
    """Renvoie le progrès du traitement de l'image en continu"""

    def generate():
        last = -1
        while True:
            if progress_data["percent"] != last:
                last = progress_data["percent"]
                yield f"data: {progress_data['percent']}|{progress_data['message']}\n\n"
            time.sleep(0.1)

    return Response(generate(), mimetype="text/event-stream")

@app.route("/color", methods=["POST"])
def color():
    """
    Renvoie le résultat du coloriage du graphe

    Parameters
    ----------
    id: str
        sha1 de l'image à colorier
    algo: str
        nom de l'algo à utiliser

    Returns
    -------
    list[dict{region_idx: color}]
        Pour chaque étapes, la couleur attribuée
    """
    id = request.json["id"]
    algo = request.json["algo"]
    print(id, algo)

    functions = {
        "random": color_random,
        "random_rules": color_random_rules,
        "glouton": color_glouton,
        "welsh_powell": color_welsh_powell,
        "dsatur": color_dsatur
    }

    if algo in functions:
        return jsonify({
            "status": "success",
            "data": functions[algo](Graphe.from_map_id(id).graphe),
        })
    else:
        return jsonify({
            "status": "error"
        }), 404

#result = Graphe.from_map_image("assets/imgs/regions_france.jpg")
#graph = result.graphe #get_regions_france()

# #color_random(graph)
# color_random_rules(graph)

#display_graph(graph)

app.run(host="0.0.0.0")