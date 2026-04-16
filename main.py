from flask import Flask, jsonify, render_template

from graph import Graphe, get_regions_france
from utils import display_graph
from color import *

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

result = Graphe.from_map_image("assets/imgs/regions_france.jpg")
graph = result.graphe #get_regions_france()

#color_random(graph)
color_random_rules(graph)

display_graph(graph)

#app.run(host="0.0.0.0")