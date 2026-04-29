from flask import Flask, render_template, request, jsonify, send_file
import json, os, uuid
from datetime import datetime
import pandas as pd
import numpy as np
from io import BytesIO

app = Flask(__name__)
DATA_FILE = "data/collectes.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    os.makedirs("data", exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/collecte")
def collecte():
    return render_template("collecte.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/api/soumettre", methods=["POST"])
def soumettre():
    d = request.json
    d["id"] = str(uuid.uuid4())[:8]
    d["date_soumission"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    records = load_data()
    records.append(d)
    save_data(records)
    return jsonify({"status": "ok", "id": d["id"]})

@app.route("/api/stats")
def stats():
    records = load_data()
    if not records:
        return jsonify({"total": 0, "cultures": {}, "regions": {}, "rendements": [], "series_temps": [], "intrants": {}, "elevage": {}})

    df = pd.DataFrame(records)

    # Cultures
    cultures = df["culture"].value_counts().to_dict() if "culture" in df else {}

    # Régions
    regions = df["region"].value_counts().to_dict() if "region" in df else {}

    # Rendements par culture
    rendements = []
    if "culture" in df and "rendement_kg_ha" in df:
        df["rendement_kg_ha"] = pd.to_numeric(df["rendement_kg_ha"], errors="coerce")
        rend = df.groupby("culture")["rendement_kg_ha"].agg(["mean","min","max","count"]).reset_index()
        rendements = rend.rename(columns={"mean":"moy","min":"min_v","max":"max_v","count":"n"}).to_dict("records")

    # Série temporelle (soumissions par mois)
    if "date_soumission" in df:
        df["mois"] = pd.to_datetime(df["date_soumission"], errors="coerce").dt.strftime("%Y-%m")
        serie = df["mois"].value_counts().sort_index().to_dict()
    else:
        serie = {}

    # Intrants
    intrants = {}
    if "engrais_kg_ha" in df:
        df["engrais_kg_ha"] = pd.to_numeric(df["engrais_kg_ha"], errors="coerce")
        intrants["engrais_moy"] = round(df["engrais_kg_ha"].mean(), 1)
    if "pesticides_l_ha" in df:
        df["pesticides_l_ha"] = pd.to_numeric(df["pesticides_l_ha"], errors="coerce")
        intrants["pesticides_moy"] = round(df["pesticides_l_ha"].mean(), 1)

    # Élevage
    elevage = {}
    if "type_elevage" in df:
        elevage["types"] = df["type_elevage"].value_counts().to_dict()
    if "nb_tetes" in df:
        df["nb_tetes"] = pd.to_numeric(df["nb_tetes"], errors="coerce")
        elevage["total_tetes"] = int(df["nb_tetes"].sum())

    # Surface totale
    surface_totale = 0
    if "surface_ha" in df:
        df["surface_ha"] = pd.to_numeric(df["surface_ha"], errors="coerce")
        surface_totale = round(df["surface_ha"].sum(), 1)

    return jsonify({
        "total": len(records),
        "cultures": cultures,
        "regions": regions,
        "rendements": rendements,
        "series_temps": serie,
        "intrants": intrants,
        "elevage": elevage,
        "surface_totale": surface_totale
    })

@app.route("/api/donnees")
def donnees():
    return jsonify(load_data())

@app.route("/api/export/excel")
def export_excel():
    records = load_data()
    if not records:
        return jsonify({"error": "Aucune donnée"}), 404
    df = pd.DataFrame(records)
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Collectes")
    buf.seek(0)
    return send_file(buf, as_attachment=True, download_name="agridata_export.xlsx",
                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

@app.route("/api/supprimer/<id>", methods=["DELETE"])
def supprimer(id):
    records = load_data()
    records = [r for r in records if r.get("id") != id]
    save_data(records)
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
