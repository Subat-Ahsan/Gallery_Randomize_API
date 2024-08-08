import os
from collections import deque

class FileRenameTreeNode:
    
    def __init__(self,val,name,count=0):
        self.val = val 
        self.name = name        
        self.nodeMap = {}
        self.count = count
         
    def __str__(self):
        string = f"{self.val}->{self.name}|"
        for v in self.nodeMap.values():
            string += f"{v.val}->{v.name},"
        string += "|"
            
        return string

"""
Stores a numerical value for each subdirectory in a directory, as well as the 
real name of the directory. Api gets numerical value, this structure is used
to get the real path of file from numerical value.
"""
class FileRenameTree:
   
    def __init__(self, numberedMap = None):
        if (numberedMap):
            self.root = FileRenameTreeNode(0, "root",numberedMap["count"])
            self.create(numberedMap)
            
        else:
            pass

    def create(self,numberedMap):
        q = deque()
        current_node = self.root
        for child in numberedMap["children"]:
            q.append((child,current_node))
        while (q):
            current, node = q.popleft()
            new_node = FileRenameTreeNode(current["pos"],current["name"],current["count"])
            node.nodeMap[current["pos"]] =  new_node
            for child in current["children"]:
                q.append((child,node.nodeMap[current["pos"]]))
            
    """
    Takes the integers representing the path in list form. Returns 
    the corresponding path in the file explorer. Ignores empty numbers
    and returns none if path is not made of integers, or can't be found.
    """
    def retrieve(self,pathlist,get_count = False):
        currentNode = self.root
        string_list = []
        for i in pathlist:
            if (i == ""): continue
            try:
                num  = int(i)
            except:
                return None

            if num in currentNode.nodeMap:
                currentNode = currentNode.nodeMap[num]
                string_list.append(currentNode.name)
            else:
                return None
        
        if (get_count):
            return (string_list, currentNode.count)
        else:
            return string_list

"""
Converts file tree starting from rootPath to a map version with nested maps for
children. Stops at certain depth and keeps track of files in each directory. 
"""
def getFolderMap(rootPath, maxdepth=-1):
    if maxdepth ==-1: maxdepth = 999

    fileTreeMap = {}
    basePath  = os.path.basename(rootPath)
    
    #Object contains {"name", "num element", "children"}
    #(Object, state, parent, path, depth
    stack = [({"name": basePath, "count": 0, "children": []},0,
            None, rootPath, 0)]        
    while (len(stack)):
        current,state,parent,path, depth = stack.pop()
        if state == 0:
            subdirs = []
            
            files_inside = 0
            try:
                for i in os.listdir(path):
                    i_path  = os.path.join(path,i)
                    if (os.path.isfile(i_path)):
                        files_inside += 1
                    elif (os.path.isdir(i_path)):
                        subdirs.append({"name": i, "count": 0, "children": []})
            except:
                return {}
            
            current["count"] += files_inside

            stack.append((current,1,parent,path,depth))
            if (depth < maxdepth):
                for i in subdirs:
                    stack.append((i,0,current,os.path.join(path,i["name"]),depth+1))
            else:
                count = 0
                for root, dirs, files in os.walk(path):
                    for f in files:
                        count += 1
                current["count"] += count
                current["count"] -= files_inside #Account for double counting
                
        else:
            for i in current["children"]:
                current["count"] += i["count"]
            if parent != None:
                parent["children"].append(current)
            else:
                return current
    return fileTreeMap

"""
Enumerates each child for easier access
"""
def getNumberedFolderMap(foldermap):
    numbered_folder_map = foldermap
    if foldermap == {}: 
        return {}
    q = deque()
    q.append(numbered_folder_map)
    while (q):
        current = q.popleft()
        count = len(current["children"])
        for i in range(count):
            child = current["children"][i]
            child["pos"] = count - i
            q.append(child)
    return numbered_folder_map

