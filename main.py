from flask import Flask, jsonify
import requests
import os

app = Flask(__name__)

# 🔑 Variables d'environnement (sécurisées via Render)
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY", "")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID", "")
NOTION_API_KEY = os.getenv("NOTION_API_KEY", "")

# 🔧 Vérification des variables d'environnement
if not AIRTABLE_API_KEY or not AIRTABLE_BASE_ID:
    print("⚠️ Erreur: Les variables AIRTABLE_API_KEY ou AIRTABLE_BASE_ID ne sont pas définies.")
if not NOTION_API_KEY:
    print("⚠️ Erreur: La variable NOTION_API_KEY n'est pas définie.")

def get_airtable_tables():
    """Récupère la liste de toutes les tables d'Airtable"""
    url = f"https://api.airtable.com/v0/meta/bases/{AIRTABLE_BASE_ID}/tables"
    headers = {"Authorization": f"Bearer {AIRTABLE_API_KEY}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json().get("tables", [])
    return {"error": f"Erreur Airtable: {response.status_code}"}

def get_airtable_data():
    """Récupère les données de toutes les tables Airtable"""
    tables = get_airtable_tables()
    all_data = {}

    for table in tables:
        table_id = table["id"]
        url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{table_id}"
        headers = {"Authorization": f"Bearer {AIRTABLE_API_KEY}"}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            all_data[table_id] = response.json().get("records", [])

    return all_data

def get_notion_databases():
    """Récupère toutes les bases Notion"""
    url = "https://api.notion.com/v1/search"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, json={"query": "", "filter": {"property": "object", "value": "database"}})

    if response.status_code == 200:
        return response.json().get("results", [])
    return {"error": f"Erreur Notion: {response.status_code}"}

@app.route("/airtable", methods=["GET"])
def airtable():
    return jsonify({"airtable_data": get_airtable_data()})

@app.route("/notion", methods=["GET"])
def notion():
    return jsonify({"notion_data": get_notion_databases()})

@app.route("/all_data", methods=["GET"])
def all_data():
    print("✅ Route /all_data appelée")  # Debug dans Render logs
    return jsonify({
        "airtable": get_airtable_data(),
        "notion": get_notion_databases()
    })

@app.route("/routes", methods=["GET"])
def show_routes():
    """Affiche toutes les routes disponibles pour debug"""
    return jsonify([rule.rule for rule in app.url_map.iter_rules()])

if __name__ == "__main__":
    print("💪 API en cours d'exécution sur Render...")
    app.run(host="0.0.0.0", port=8080)
