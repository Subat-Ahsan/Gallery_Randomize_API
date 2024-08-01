from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse, FileResponse
import random
import uvicorn
import configparser
import os

from parse_folder import *

from fastapi.middleware.cors import CORSMiddleware

config = configparser.ConfigParser()
config.read('config.ini')
directory =  os.path.abspath(config["DEFAULT"]["folderName"])
depth =  int(config["DEFAULT"]["depth"])

app = FastAPI()
files_data = None
files_name_tree = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
def home():
    return "Random Image Generator API"

@app.get("/data")
def getCurrentData():
    return files_data

@app.get("/image")
def getImage(d: str = Query(None)):
    image_path = ""
    directories = []
    if (files_name_tree == None or files_data == None):
        return {"Error": "No Data"}
    
    count = 0
    if (d == None):
        directories.append(directory)
        count = files_data["count"]
    else:
        
        directory_query = d.split(",")
        for s in directory_query:
            converted_dir = files_name_tree.retrieve(s.split("/"),True)
            
            if (converted_dir != None):
                path_list, items = converted_dir
                path = os.path.join(directory, *path_list)
                directories.append(path)
                count += items

    r = random.randint(1,count)
    count2 = 0
    for d in directories:
        for root, dirs, files in os.walk(d):
            for name in files:
                count2 += 1
                if (count2 == r):   
                    image_path = os.path.join(root, name)

     
    if image_path == "":
        return {"Error:", "Image Not Found"}
    else:
        return FileResponse(image_path)

if __name__ == "__main__":

    files_data = getNumberedFolderMap(getFolderMap(directory,depth))
    print(files_data)
    files_name_tree = FileRenameTree(files_data)
    uvicorn.run(app, host="127.0.0.1", port=8000)