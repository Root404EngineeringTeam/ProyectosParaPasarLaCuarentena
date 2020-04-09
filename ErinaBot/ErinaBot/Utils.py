import random
import unidecode

from requests import get
from bs4 import BeautifulSoup

def covid_cases(search):
    response = get("https://docs.google.com/spreadsheets/d/e/2PACX-1vR30F8lYP3jG7YOq8es0PBpJIE5yvRVZffOyaqC0GgMBN6yt0Q-NI8pxS7hd1F9dYXnowSC6zpZmW9D/pubhtml?gid=0&amp;single=true&amp;widget=true&amp;headers=false&amp;range=A1:I202")

    soup = BeautifulSoup(response.text, 'lxml')
    tables = soup.find_all("table")
    rows = tables[0].find_all("tr")

    search = search.replace("_"," ")

    for row in rows:
        cells = row.find_all("td")
        cells = [unidecode.unidecode(cell.text.strip()) for cell in cells]

        try:
                country = cells[0]
                confirmed = cells[1]
                deaths = cells[3]
                serious = cells[6]
                recovered = cells[7]

                if country.lower() == unidecode.unidecode(search.lower()):
                    return "Casos de Covid-19 en **%s** : %s confirmados %s muertes %s graves %s recuperados\n" % (country, confirmed, deaths, serious, recovered)

        except Exception as e:
            pass

    return "Lo siento no pude obtener los datos en este momento :( meper donas?"

def get_nudes(topic):
    response = get("https://rule34.xxx/index.php/index.php?page=dapi&s=post&q=index&tags=%s&limit=50&pid=%s" %(topic, random.randrange(0,88)))

    soup = BeautifulSoup(response.text, 'lxml')
    posts = soup.find_all("post")

    try:
        post = random.choice(posts)

    except:
        return "No encontre ninguno de %s :c" %(topic)

    return post['file_url']

def get_meme():
    n = random.randint(1, 200)
    response = get("https://es.memedroid.com/memes/random/%s" %(n))

    soup = BeautifulSoup(response.text, 'lxml')
    articles = soup.findAll('article', attrs={'class': 'gallery-item'})

    article = random.choice(articles)
    img = article.find('img')
    meme = img['src']

    return meme

def get_joke():
    response = get("http://www.chistes.com/chistealazar.asp")

    soup = BeautifulSoup(response.text, 'lxml')
    box = soup.find('div', attrs={'class': 'chiste'})

    return box.text
