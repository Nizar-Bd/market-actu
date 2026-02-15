import json, os, shutil
from bs4 import BeautifulSoup
from curl_cffi import requests
from datetime import datetime

TARGETS = {
    'commodity/': ["brent-crude-oil", "gold", "eu-natural-gas"],
    'united-states/': ["stock-market"],
    'france/': ["stock-market"],
    'germany/': ["stock-market"],
    'united-kingdom/': ['stock-market'],
    'euro-area/': ["stock-market"],
}

def fetch_market_data(url):

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/"
        }

    res = requests.get(url, impersonate='chrome120', headers=headers)

    if res.status_code != 200:
        raise Exception(f"HTTP Status {res.status_code}")

    soup = BeautifulSoup(res.content, 'html.parser')

    try:
        summary = soup.find("h2", id="description").text.strip()
        updated = soup.find("small", class_="te-stream-date").text.strip()
        scripts = soup.find_all("script", language="Javascript")
        raw_js = next(s.text for s in scripts if s.string and "TEChartsMeta" in s.string)
        val = float(raw_js.split('"value":')[1].split(',')[0])
    except Exception as e:
        print(soup.title.text.strip() if soup.title else f"No title for {url}")
        print(e)

    return summary, updated, val

def main():
    history_file = 'market_history.json'
    history = {}
    if os.path.exists(history_file):
        with open(history_file, 'r') as f:
            history = json.load(f)

    new_data = {}
    rows_html = ""

    for path, assets in TARGETS.items():
        for asset in assets:
            url = f"{path}{asset}"
            try:
                txt, date, val = fetch_market_data(f"https://tradingeconomics.com/{url}")
                new_data[url] = val

                # Variation logic
                prev = history.get(url)
                delta_html = '<span style="color:gray">N/A</span>'
                if prev:
                    diff = ((val - prev) / prev) * 100
                    color = "#2ecc71" if diff >= 0 else "#e74c3c"
                    delta_html = f'<b style="color:{color}">{"+" if diff>0 else ""}{diff:.2f}%</b>'

                rows_html += f"""
                <article>
                    <header><strong>{asset.replace("-", " ").upper()}</strong></header>
                    <div class="grid">
                        <div><small>Price</small><br><strong>{val}</strong></div>
                        <div><small>24h Var.</small><br>{delta_html}</div>
                        <div><small>Updated</small><br><small>{date}</small></div>
                    </div>
                    <p style="font-size: 0.85rem; margin: 10px 0;">{txt}</p>
                    <footer><a href="https://tradingeconomics.com/{url}">View on Trading Economics</a></footer>
                </article>"""
            except Exception as e:
                print(f"Failed {url}: {e}")

    # UI Template
    now = datetime.now().strftime('%d %b %Y')
    html = f"""<!DOCTYPE html><html lang="en" data-theme="dark">
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css">
        <link rel="icon" href="https://fav.farm/📈" />
        <title>Markets | {now}</title>
    </head>
    <body class="container" style="padding:20px 0">
        <hgroup><h1>📈 Market Actu</h1><p>Snapshot: {now}</p></hgroup>
        <hr>{rows_html}
    </body></html>"""

    # Files management
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    os.makedirs("archives", exist_ok=True)
    shutil.copy("index.html", f"archives/review_{datetime.now().strftime('%Y_%m_%d')}.html")

    with open(history_file, 'w') as f:
        json.dump(new_data, f, indent=2)

if __name__ == "__main__":
    main()
