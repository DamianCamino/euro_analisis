# Diccionario de traducciones para la aplicación
translations = {
    "es": {
        "title": "Mapa movilidad UE",
        "click_country": "Click en un país",
        "reception": "Recepción",
        "emission": "Emisión",
        "total": "Total",
        "no_data": "No hay datos en European Data Portal",
        "total_countries": "Total países creados",
        "countries": {
            "AT": "Austria",
            "BE": "Bélgica",
            "BG": "Bulgaria",
            "CY": "Chipre",
            "CZ": "República Checa",
            "CZ_SK": "República Checa",
            "DE": "Alemania",
            "DK": "Dinamarca",
            "EE": "Estonia",
            "EL": "Grecia",
            "ES": "España",
            "FI": "Finlandia",
            "FR": "Francia",
            "HR": "Croacia",
            "HU": "Hungría",
            "IE": "Irlanda",
            "IT": "Italia",
            "LT": "Lituania",
            "LU": "Luxemburgo",
            "LV": "Letonia",
            "MT": "Malta",
            "NL": "Países Bajos",
            "PL": "Polonia",
            "PT": "Portugal",
            "RO": "Rumania",
            "SE": "Suecia",
            "SI": "Eslovenia",
            "SK": "Eslovaquia",
        }
    },
    "en": {
        "title": "EU Mobility Map",
        "click_country": "Click on a country",
        "reception": "Immigration",
        "emission": "Emigration",
        "total": "Total",
        "no_data": "No data available in European Data Portal",
        "total_countries": "Total countries created",
        "countries": {
            "AT": "Austria",
            "BE": "Belgium",
            "BG": "Bulgaria",
            "CY": "Cyprus",
            "CZ": "Czech Republic",
            "CZ_SK": "Czech Republic",
            "DE": "Germany",
            "DK": "Denmark",
            "EE": "Estonia",
            "EL": "Greece",
            "ES": "Spain",
            "FI": "Finland",
            "FR": "France",
            "HR": "Croatia",
            "HU": "Hungary",
            "IE": "Ireland",
            "IT": "Italy",
            "LT": "Lithuania",
            "LU": "Luxembourg",
            "LV": "Latvia",
            "MT": "Malta",
            "NL": "Netherlands",
            "PL": "Poland",
            "PT": "Portugal",
            "RO": "Romania",
            "SE": "Sweden",
            "SI": "Slovenia",
            "SK": "Slovakia",
        }
    }
}

def t(key, lang="es"):
    """Función auxiliar para obtener traducciones"""
    keys = key.split(".")
    current = translations.get(lang, translations["es"])
    
    for k in keys:
        if isinstance(current, dict):
            current = current.get(k)
        else:
            return key
    
    return current if current is not None else key
