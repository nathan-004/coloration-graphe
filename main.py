from flask import Flask, render_template, request, Response, jsonify
from flask import Blueprint, abort
import os
import time
import json

from graph import Graphe, get_regions_france
from utils import display_graph, progress_data
from color import *

app = Flask(__name__)

imgs = Blueprint("imgs", __name__, static_url_path="/imgs", static_folder="saves/imgs")
app.register_blueprint(imgs)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/maps")
def maps():
    return render_template("maps.html")

@app.route("/maps/<id>")
def map(id):
    path = f"saves/{id}.json"
    if not os.path.isfile(path):
        abort(404)
    with open(path) as f:
        centers = json.load(f)["centers"]
    return render_template("map.html", id=id, centers=centers)

@app.route("/upload")
def upload():
    return render_template("upload.html")

@app.route("/upload-map", methods=["POST"])
def upload_map():
    file = request.files["file"]
    path = "assets/temp"
    i = 0

    while os.path.isfile(path + str(i) + ".png"):
        i += 1
    path = path + str(i) + ".png"

    file.save(path)

    result = Graphe.from_map_image(path)

    os.remove(path)

    return jsonify({
        "status": "success",
        "data": result.map_id
    })

@app.route("/progress")
def progress():
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