from fastapi import FastAPI
from fastapi.responses import FileResponse
import requests
import pandas as pd

app = FastAPI()

@app.get("/drinks", response_class=FileResponse, tags=["DRINKS"])
async def get_drinks():
    url = "https://www.thecocktaildb.com/api/json/v1/1/filter.php?a=Alcoholic"

    r = requests.get(url)
    response = {}
    for drink in r.json()["drinks"]:
        response[drink["strDrink"]] = {}
        response[drink["strDrink"]]["name"] = drink["strDrink"]
        response[drink["strDrink"]]["id"] = drink["idDrink"]

    # Convertir el JSON a DataFrame
    df = pd.DataFrame(response.values())
    file_name = 'api_drinks.csv'
    # Guardar el DataFrame como CSV
    df.to_csv(file_name, index=False)

    return FileResponse(file_name, filename=file_name)


#if __name__ == "__main__":
#    uvicorn.run(app, host="0.0.0.0", port=8000)