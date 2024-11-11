import base64, os
from bson import ObjectId
from fastapi import FastAPI, File, Form, Response, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from typing_extensions import Annotated
from typing import List, Union
from server.db import connect_db
from server.data import mock_data
from dotenv import load_dotenv

load_dotenv("miniofconfig.env")

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

connection = connect_db()
db = connection.get_database("FilesDatabase")
coll = db.get_collection("uploadedfiles")

def helper_struct(obj) -> dict:
    return {
        "id": str(obj["_id"]),
        "name": obj["name"],
        "price": obj["price"],
        "image": base64.b64encode(obj["image"])
    }

def type_data(obj) -> dict:
    return {
        "id": str(obj["_id"]),
        "filename": obj["filename"],
        "file": obj["file"]
    }

# return response on root
@app.get("/")
def readroot():
    return {"response": "hello world"}

# return data from mongodb
@app.get("/mongodata")
async def get_data_by_id_or_all(id: Union[str, None] = None):
    data = []
    if id is None:
        async for doc in coll.find():
            data.append(helper_struct(doc))
        return data
    record = await coll.find_one({"_id": ObjectId(id)})
    if record:
        return helper_struct(record) 
    else:
        return "no record found"

# return mock json data
@app.get('/data')
def mock_json_data():
    return mock_data

# return files from mongodb
@app.get("/files")
async def get_data():
    try:
        data = []
        async for doc in coll.find():
            data.append(type_data(doc))
        return data
    except Exception as e:
        return "Error occurred" + str(e) 
    

#post with image
@app.post("/")
async def post_data(itemname: Annotated[str, None], itemprice: Annotated[int, None], itemImage: Annotated[bytes, File()] = None):
    record = await coll.insert_one({
        "name": itemname,
        "price": itemprice,
        "image": itemImage
    })
    if record:
        return "data posted"
    else:
        return "error in posting data"

# post files in mongodb
@app.post("/files")
async def post_data(files: List[UploadFile]):
    try:
        for file in files:
            await coll.insert_one({
            "file": file.file.read(),
            "filename": file.filename, 
            "filesize": file.size
            })
        return "posted"
    except Exception as e:
        return "error" + str(e)
     
# update files in mongodb
@app.put("/")
async def update_records(id: str, itemname: str, itemprice: Annotated[int, None], itemImage: Annotated[bytes, File()] = None):
    record = await coll.find_one({"_id": ObjectId(id)})
    result = False
    if record:
        updated_record = await coll.update_one(
            {"_id": ObjectId(id)}, {"$set": {"name": itemname, "price": itemprice, "image": itemImage}}
        )
        if updated_record:
            result = True
    if result:
        return Response("Record Updated", status_code=200)
    else:
        return Response("Error updating record", status_code=500)

# delete files 
@app.delete("/{id}")
async def delete_record(id: str):
    try:
        record = await coll.find_one({"_id": ObjectId(id)})
        if record:
            await coll.delete_one(record)
            return "record deleted"
    except Exception as e:
        return Response("Error in deleting record", status_code=500)
    


