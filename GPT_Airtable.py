from flask import Flask, jsonify
import requests

app = Flask(__name__)

# 🔑 Airtable API
AIRTABLE_API_KEY = "patpXhUKeWRQUFHhd.573761d470482ee493fc6a1ab12cc700e9117e652e8a89fdf7bbeba8f5381ebc"
BASE_ID = "app1Is4nM36uamO8B"

# 🔑 Notion API
NOTION_API_KEY = "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"

def get_airtable_tables():
    """Récupérer la liste de toutes les tables d'Airtable"""
    url = f"https://api.airtable.com/v0/meta/bases/{BASE_ID}/tables"
    headers = {"Authorization": f"Bearer {AIRTABLE_API_KEY}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        tables = response.json().get("tables", [])
        return [table["id"] for table in tables]
    
    return {"error": f"Erreur lors de la récupération des tables d'Airtable: {response.status_code}"}

def get_airtable_data():
    """Récupérer les données de toutes les tables Airtable"""
    tables = get_airtable_tables()
    all_data = {}

    for table_id in tables:
        url = f"https://api.airtable.com/v0/{BASE_ID}/{table_id}"
        headers = {"Authorization": f"Bearer {AIRTABLE_API_KEY}"}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            records = response.json().get("records", [])
            all_data[table_id] = [record["fields"] for record in records]

    return all_data

def get_notion_databases():
    """Récupérer toutes les bases Notion"""
    url = "https://api.notion.com/v1/search"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, json={"query": "", "filter": {"property": "object", "value": "database"}})

    if response.status_code == 200:
        results = response.json().get("results", [])
        return [db["id"] for db in results]
    
    return {"error": f"Erreur lors de la récupération des bases Notion: {response.status_code}"}

def get_notion_data():
    """Récupérer toutes les données des bases Notion"""
    databases = get_notion_databases()
    all_data = {}

    for db_id in databases:
        url = f"https://api.notion.com/v1/databases/{db_id}/query"
        headers = {
            "Authorization": f"Bearer {NOTION_API_KEY}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
        response = requests.post(url, headers=headers)

        if response.status_code == 200:
            results = response.json().get("results", [])
            data = []
            for item in results:
                properties = item.get("properties", {})
                entry = {}
                for key, value in properties.items():
                    if "title" in value and value["title"]:
                        entry[key] = value["title"][0]["text"]["content"]
                    elif "rich_text" in value and value["rich_text"]:
                        entry[key] = value["rich_text"][0]["text"]["content"]
                    elif "number" in value:
                        entry[key] = value["number"]
                    elif "checkbox" in value:
                        entry[key] = value["checkbox"]
                    elif "date" in value and value["date"]:
                        entry[key] = value["date"]["start"]
                    else:
                        entry[key] = "Inconnu"
                data.append(entry)
            all_data[db_id] = data

    return all_data

@app.route("/airtable", methods=["GET"])
def airtable():
    return jsonify({"airtable_data": get_airtable_data()})

@app.route("/notion", methods=["GET"])
def notion():
    return jsonify({"notion_data": get_notion_data()})

@app.route("/all_data", methods=["GET"])
def all_data():
    return jsonify({
        "airtable": get_airtable_data(),
        "notion": get_notion_data()
    })

if __name__ == "__main__":
    app.run(port=5000)
