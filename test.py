import requests
from deep_translator import GoogleTranslator

sign_map = {
    "belier": "aries",
    "bélier": "aries",
    "taureau": "taurus",
    "gemeaux": "gemini",
    "gémeaux": "gemini",
    "cancer": "cancer",
    "lion": "leo",
    "vierge": "virgo",
    "balance": "libra",
    "scorpion": "scorpio",
    "sagittaire": "sagittarius",
    "capricorne": "capricorn",
    "verseau": "aquarius",
    "poissons": "pisces"
}

ACCENTS = "éèêëàâäùûüôöç"
REPLACEMENTS = "eeeeaaauuuooc"

def remove_accents(text):
    translation_table = str.maketrans(ACCENTS, REPLACEMENTS)
    return text.translate(translation_table)

def get_horoscope(sign_fr, day="TODAY"):
    sign_key = sign_fr.lower()
    sign_key = remove_accents(sign_key)

    sign_en = sign_map.get(sign_key)
    if not sign_en:
        return f"Signe astrologique '{sign_fr}' non reconnu."

    url = f"https://horoscope-app-api.vercel.app/api/v1/get-horoscope/daily?sign={sign_en.capitalize()}&day={day.upper()}"
    response = requests.get(url)

    if response.status_code == 200:
        json_data = response.json()
        if json_data.get("success"):
            horoscope = json_data["data"]["horoscope_data"]
            date = json_data["data"]["date"]
            translated_horoscope = GoogleTranslator(source='en', target='fr').translate(horoscope)
            return f"Horoscope du jour pour {sign_fr.capitalize()} :\n{translated_horoscope}"
        else:
            return "Erreur : réponse non réussie de l'API."
    else:
        return f"Erreur HTTP {response.status_code} lors de la récupération."

if __name__ == "__main__":
    signe_fr = "Gémeaux"
    print(get_horoscope(signe_fr))
