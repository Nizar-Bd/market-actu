from bs4 import BeautifulSoup
from curl_cffi import requests
from datetime import datetime

base_url = "https://tradingeconomics.com/"
target_data = {'commodity/' : ["brent-crude-oil", # Barril de pétrole
                               "gold", # Or
                               "eu-natural-gas"], # Gaz naturel en Europe
               'united-states/' : ["stock-market"], #S&P50
               'france/' : ["stock-market"], # CAC40
               'germany/' : ["stock-market"], # DAX40
               'united-kingdom/' : ['stock-market'], # FTSE100
               'euro-area/' : ["stock-market"], # EU50
               }

def get_summary(url):

    response = requests.get(url, impersonate='chrome')
    soup = BeautifulSoup(response.content, 'html.parser')

    return soup.find("h2", id="description").text, soup.find("small", class_="te-stream-date").text

def get_all():
    body = f"<h2>Point Marché du {datetime.now().strftime('%d/%m/%Y')}</h2><hr>"
    for cat in target_data :
        for asset in target_data[cat] :

            title = cat + asset
            url = base_url + title

            summary, date = get_summary(url)

            body  += f"""<p>
                            <strong>{title + " " + date}</strong> <br>
                            <a href="{url}">{url}</a> <br><br>
                            {summary}
                        </p>
                        <hr>
                      """

    with open(f"index.html", "w", encoding="utf-8") as f:
        f.write(body)


if __name__ == "__main__":
    get_all()
