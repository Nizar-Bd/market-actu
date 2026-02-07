import json
import os
import shutil
from bs4 import BeautifulSoup
from curl_cffi import requests
from datetime import datetime

base_url = "https://tradingeconomics.com/"
target_data = {
    'commodity/': ["brent-crude-oil", "gold", "eu-natural-gas"],
    'united-states/': ["stock-market"],
    'france/': ["stock-market"],
    'germany/': ["stock-market"],
    'united-kingdom/': ['stock-market'],
    'euro-area/': ["stock-market"],
}

def get_summary(url):
    response = requests.get(url, impersonate='chrome')
    soup = BeautifulSoup(response.content, 'html.parser')

    summary = soup.find("h2", id="description").text.strip()
    date_stream = soup.find("small", class_="te-stream-date").text.strip()

    # Extraction de la valeur via le script JS
    scripts = soup.find_all("script", language="Javascript")
    # On cherche le script qui contient TEChartsMeta
    target_script = next(s.text for s in scripts if s.string and "TEChartsMeta" in s.string)

    value = float(target_script.split('"value":')[1].split(',')[0])
    return summary, date_stream, value

def load_history():
    if os.path.exists('market_history.json'):
        with open('market_history.json', 'r') as f:
            return json.load(f)
    return {}

def save_history(history):
    with open('market_history.json', 'w') as f:
        json.dump(history, f, indent=4)

def get_all():
    history = load_history()
    new_history = {}
    now = datetime.now().strftime('%d/%m/%Y %H:%M')

    # Début du HTML avec Pico.css
    rows_html = ""

    for cat in target_data:
        for asset in target_data[cat]:
            asset_id = f"{cat}{asset}"
            url = base_url + asset_id

            try:
                summary, date_stream, value = get_summary(url)

                # Calcul de la variation sur 24h (via JSON)
                last_value = history.get(asset_id)
                if last_value:
                    diff = ((value - last_value) / last_value) * 100
                    color = "#2ecc71" if diff >= 0 else "#e74c3c"
                    sign = "+" if diff >= 0 else ""
                    variation_html = f'<span style="color: {color}; font-weight: bold;">{sign}{diff:.2f}%</span>'
                else:
                    variation_html = '<span style="color: gray;">N/A</span>'

                new_history[asset_id] = value

                # Construction de la ligne du tableau
                rows_html += f"""
                <article>
                    <header><strong>{asset_id.upper()}</strong></header>
                    <div class="grid">
                        <div><small>Valeur:</small><br><strong>{value}</strong></div>
                        <div><small>Var. 24h:</small><br>{variation_html}</div>
                        <div><small>Source:</small><br><small>{date_stream}</small></div>
                    </div>
                    <p style="margin-top: 10px; font-size: 0.9em;">{summary}</p>
                    <footer><a href="{url}" target="_blank">Voir sur Trading Economics</a></footer>
                </article>
                """
            except Exception as e:
                print(f"Erreur sur {asset_id}: {e}")

    # Template final propre avec Pico.css
    full_html = f"""
    <!DOCTYPE html>
    <html lang="fr" data-theme="dark">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css">
        <title>Market Review Daily</title>
        <style>
            body {{ padding: 20px 0; }}
            article {{ margin-bottom: 2rem; }}
        </style>
    </head>
    <body>
        <main class="container">
            <hgroup>
                <h1>📊 Market Actu</h1>
                    <h4>⚙️ by Nizar-Bd</h4>
                <p>Dernière mise à jour : {now}</p>
            </hgroup>
            <hr>
            {rows_html}
        </main>
    </body>
    </html>
    """

    # 1. Sauvegarde du fichier principal
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(full_html)

    # 2. Archivage
    if not os.path.exists("archives"):
        os.makedirs("archives")

    archive_name = f"review_{datetime.now().strftime('%d_%m_%Y')}.html"
    shutil.copy("index.html", os.path.join("archives", archive_name))

    # 3. Sauvegarde de l'historique numérique
    save_history(new_history)

if __name__ == "__main__":
    get_all()
