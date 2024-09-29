from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import json
from data_analysis import AnalysisData

from config import SECRET_TOKEN


class Item(BaseModel):
    title: str
    description: str
    category: str
    location: str 

class Item2(BaseModel):
    get: int

app = FastAPI()

@app.post("/dangerIndex/get")
async def process_data(item: Item):
    ad = AnalysisData(SECRET_TOKEN)
    danger_index = ad.get_danger_level(title=item.title, location=item.location, description=item.description, category=item.category)

    result = {
        "dangerIndex": danger_index
    }

    return result

@app.post("/news/data/get")
async def process_data(item: Item2):
    try:
        with open('data/datasest.json', 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
    except FileNotFoundError:
        data = {
            "data": 'not data'
        }

    result = data

    return result

if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)
