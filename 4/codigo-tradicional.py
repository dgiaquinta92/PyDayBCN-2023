import requests
import pandas as pd

url = "https://www.thecocktaildb.com/api/json/v1/1/filter.php?a=Alcoholic"
r = requests.get(url)
response = {}

for drink in r.json()["drinks"]:
    response[drink["strDrink"]] = {}
    response[drink["strDrink"]]["name"] = drink["strDrink"]
    response[drink["strDrink"]]["id"] = drink["idDrink"]

# Convertir el JSON a DataFrame
df = pd.DataFrame(response.values())

file_name = '4/drinks.csv'

# Guardar el DataFrame como CSV
df.to_csv(file_name, index=False)
