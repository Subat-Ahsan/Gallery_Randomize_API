from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse, FileResponse
import random
import uvicorn
import configparser
import os
import asyncio

from parse_folder import *

from fastapi.middleware.cors import CORSMiddleware

config = configparser.ConfigParser()
config.read('config.ini')
directory =  os.path.abspath(config["DEFAULT"]["folderName"])
depth =  int(config["DEFAULT"]["depth"])
url = config["DEFAULT"]["url"]
port = int(config["DEFAULT"]["port"])


app = FastAPI()
files_data = None
files_name_tree = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
    expose_headers = ["path", "pos"]
)

        
@app.get("/")
def home():
    return "Random Image Generator API"

"""
Returns data of each directory as json. 
"""
@app.get("/data")
def getCurrentData():
    return files_data

"""
Returns a random image from the specified root directory. Includes it's path from
the root as the header path. Subdirectories can be filtered, and specific image
can be selected. 
"""
@app.get("/image")
async def getImage(dirs: str = Query(None), num: int = Query(0)):
    image_path = ""
    directories = []
    if (files_name_tree == None or files_data == None):
        return {"Error": "No Data"}
    
    count = 0
    if (dirs == None):
        directories.append(directory)
        count = files_data["count"]
    else:
        
        directory_query = dirs.split(",")
        for s in directory_query:
            converted_dir = files_name_tree.retrieve(s.split("/"),True)
            
            if (converted_dir != None):
                path_list, items = converted_dir
                path = os.path.join(directory, *path_list)
                directories.append(path)
                count += items

    if (num <= 0):
        r = random.randint(1,count)
    else:
        r = (num-1) % (count) + 1

    count2 = 0
    relative_path = ""
    r_break = False
    for d in directories:
        for root, dirs, files in os.walk(d):
            for name in files:
                count2 += 1
                if (count2 == r):   
                    image_path = os.path.join(root, name)
                    relative_path = os.path.dirname(os.path.relpath(image_path,directory))
                    r_break = True
                    if (r_break) : break
            if (r_break) : break
        if (r_break) : break
        
    
    headers = {"path": relative_path, "last-modified" : "", "pos":str(count2)}

    if image_path == "":
        return {"Error:", "Image Not Found"}
    else:
        return FileResponse(image_path, headers=headers)

if __name__ == "__main__":

    files_data = getNumberedFolderMap(getFolderMap(directory,depth))
    print(files_data)
    files_name_tree = FileRenameTree(files_data)
    print(f"\nRunning API on {url}:{port}")

    uvicorn.run(app, host=url, port=port, log_level="warning")  
    