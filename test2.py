import requests
from deep_translator import GoogleTranslator

def get_quote_of_the_day():
    url = "https://zenquotes.io/api/today"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            quote = data[0]["q"]
            author = data[0]["a"]
            translated_horoscope = GoogleTranslator(source='en', target='fr').translate(quote)
            return f"« {translated_horoscope} » — {author}"
        else:
            return f"Erreur HTTP {response.status_code} lors de la récupération."
    except Exception as e:
        return f"Erreur lors de la requête : {e}"

if __name__ == "__main__":
    print(get_quote_of_the_day())
