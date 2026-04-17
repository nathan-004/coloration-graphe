from flask import Flask, render_template, request, Response, jsonify
import os
import time

from graph import Graphe, get_regions_france
from utils import display_graph, progress_data
from color import *

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/maps")
def maps():
    return render_template("maps.html")

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

# result = Graphe.from_map_image("assets/imgs/regions_france.jpg")
# graph = result.graphe #get_regions_france()

# #color_random(graph)
# color_random_rules(graph)

# display_graph(graph)

app.run(host="0.0.0.0")