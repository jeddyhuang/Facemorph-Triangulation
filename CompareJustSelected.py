import numpy as np
import matplotlib.pyplot as plt
import linecache
import datetime
import os
from meshLoopBackPolygonFunction import *

# Path to selected OBJ
MYOBJPATH = ".\\TestData\\Together\\A\\A.obj"
# Path to OBJS
OBJPATH = ".\\TestData\\Together"
# Path to Selected Landmark Points
SELPATH = ".\\TestData\\Selected Points"
# Path to Triangles file
# This one is predetermined and not changed by the Config File
# Read from config anyway? 
TRIPATH = ".\\MyTriangles-Chin.txt"
# Path to File containing Specific Polygons to look at
PLYPATH = ".\\RegionsToCompare.txt"

# Reads the OBJ files provided
# I am using the linecache module, hopefully to avoid having the entire OBJ file in memory.
def readObjFile(_objPath, _selPath):
    fullData = {}
    # Selected Point is the index list of the Landmark Points in the obj File
    # Get the Vertexes from the Obj File
    SelectedPath = _selPath
    #objPath = _objPath
    #print(objPath)
    SelectedFile = open(SelectedPath, 'r')
    #ObjectFile = open(objPath, 'r')
    for line in SelectedFile:
        index = line.split()
        #print(index)
        data = linecache.getline(_objPath, int(index[1]) + 1).split()
        #print(data)
        fullData[index[0]] = [float(data[1]), float(data[2]), float(data[3][:-1])] # Remove Newline char from end of z data
    SelectedFile.close()
    #objFile.close()
    return(fullData)

# Expects a file where the Landmark Point names are listed 3 on a line, seperated by spaces.
# The file represents the triangulation of the landmark points
# Comments can start with a #. Everything after the # is ignored.
def readFaceFile(path):
    faceData = []
    file = open(path, 'r')
    for line in file:
        newLine = line.split("#")
        if newLine[0] != "":
            data = newLine[0].split()
            faceData.append(data)

    file.close()
    #print(faceData)
    return faceData
   
# Expects Data formatted in the same way as the Face File. -> readFaceFile(path)
# The largest Polygon selected will determine complexity of runtime.
#   `-> Need to test impact of large order polygons.
def readSelectedPolygonFile(path):
    selectedGroups = []
    file = open(path, 'r')
    largestPoly = 0
    for line in file:
        newLine = line.split("#")
        if newLine[0] != "":
            data = newLine[0].split()
            if len(data) > largestPoly:
                largestPoly = len(data)
            selectedGroups.append(data)
            
    file.close()
    return(selectedGroups, largestPoly)
    
def readConfigFile(path):
    global MYOBJPATH
    global OBJPATH
    global SELPATH
    global PLYPATH
    
    try:
        file = open(path, 'r')
        MYOBJPATH = file.readline().strip()
        OBJPATH = file.readline().strip()
        SELPATH = file.readline().strip()
        PLYPATH = file.readline().strip()
        
        print(MYOBJPATH)
        print(OBJPATH)
        print(SELPATH)
        print(PLYPATH)
    except:
        print("Error reading Config file.")
        return False
        
    return True

# This just formats the data array into a numpy data structure.
# This might not be necessary, but matplotlib seems to like numpy arrays.
def makeNPArray(fullData):
    formattedData = []
    for key,val in fullData.items():
        formattedData.append(val)
    data = np.array(formattedData)
    #print(data)
    return(data)
    
# This formats data to be used with matplotlib.
# I'll have to look it up again to understand it...
def makeDrawList(fullData, sim, semi, dis):
    # Will have to make triangles seperately, to avoid lots of extra lines
    polys = []

    for f in dis:
        polys.append([[],[], ''])
        drawCounter = 0
        while drawCounter < (len(f) + 1):
            polys[-1][0].append(fullData[f[drawCounter % (len(f) - 1)]][0])
            polys[-1][1].append(fullData[f[drawCounter % (len(f) - 1)]][1])
            drawCounter += 1
        # Color Val
        polys[-1][2] = 'r-'#Color for red

    for f in semi:
        polys.append([[],[], ''])
        # X coords
        drawCounter = 0
        while drawCounter < (len(f) + 1):
            polys[-1][0].append(fullData[f[drawCounter % (len(f) - 1)]][0])
            polys[-1][1].append(fullData[f[drawCounter % (len(f) - 1)]][1])
            drawCounter += 1
        # Color Val
        polys[-1][2] = 'y-'#Color for yellow
        
    for f in sim:
        polys.append([[],[], ''])
        # X coords
        drawCounter = 0
        while drawCounter < (len(f) + 1):
            polys[-1][0].append(fullData[f[drawCounter % (len(f) - 1)]][0])
            polys[-1][1].append(fullData[f[drawCounter % (len(f) - 1)]][1])
            drawCounter += 1
        # Color Val
        polys[-1][2] = 'g-'#Color for green

    return(polys)

# Determine how many faces are in the OBJPATH subfolders
# Just burrow down and grab any file with an OBJ extension?    
def getNestedOBJFiles(path):
    objFullPaths = []
    try:
        dirs = os.listdir(path)
    except:
        print(path + " Is not a Directory.")
        return objFullPaths # Make sure empty list is returned in this case to avoid potential errors
        
    for item in dirs:
        if(".obj" in item.lower()):
            objFullPaths.append(path + "\\" + item)
        elif("." in item):
            pass # This is just another file, not an obj one.
        else:
            # This probably means the file is a directory, try changing into this one.
            for nestedItem in getNestedOBJFiles(path + "\\" + item):
                objFullPaths.append(nestedItem)
    
    return objFullPaths
    
# This method is different than above. 
# It takes the result of getNestedOBJFiles and finds the associated .txt file containing the selected landmark points.
# This expects all "Selected Landmark Points" files to be in the same directory
def getSelectedPointFiles(path, objFilePaths):
    selFullPaths = []
    names = []
    for objFile in objFilePaths:
        objName = objFile[objFile.rfind("\\") + 1 : objFile.rfind(".")]
        names.append(objName)
        selName = objName + ".txt"
        print(objName, selName)
        selFullPaths.append(path + "\\" + selName)
        
    return selFullPaths, names
    
def runCompareScript():
    print(datetime.datetime.now())
    if(not readConfigFile(".\\files.cfg")):
        return -1
    print("Scanning " + OBJPATH + " for .obj files.")
    #print("TEMP MESSAGE: If errors occur, make sure SELPATH and OBJPATH point to different directories.") # This shouldn't be an issue?
    objFiles = getNestedOBJFiles(OBJPATH)
    selFiles, names = getSelectedPointFiles(SELPATH, objFiles)
        
    #print(objFiles)
    #print(selFiles)
    print("Ready to Read File for Mesh Comparison")
    allFullData = []
    myObjIndex = -1
    for i in range(len(objFiles)):
        #print(objFiles[i], selFiles[i])
        if(MYOBJPATH == objFiles[i].replace("\\", "/")): # weird path stuff because of file dialogs
            myObjIndex = i
        allFullData.append(readObjFile(objFiles[i], selFiles[i]))
    
    """
    fullDataA = readObjFile(FirstFace)
    fullDataB = readObjFile(SecondFace)

    npDataA = makeNPArray(fullDataA)
    xa, ya, za = npDataA.T
    npDataB = makeNPArray(fullDataB)
    xb, yb, zb = npDataB.T

    plt.subplot(3,2,1)
    plt.scatter(xa, ya)
    plt.title("Face A")
    #print(npDataA)

    plt.subplot(3,2,2)
    plt.scatter(xb, yb)
    plt.title("Face B")
    """
    
    meshes = []
    print("Making Mesh Objects")
    faceData = readFaceFile(TRIPATH)
    for i in range(len(allFullData)):
        try:
            m = Mesh(faceData, "mesh-" + names[i])
            m.makeMesh(allFullData[i])
            meshes.append(m)
        except:
            print("Mesh from " + selFiles[i] + " Cannot be created")
            
    for mesh in meshes:
        print(mesh.name)
    
    """
    m = Mesh("mesh-1")
    m.makeMesh(fullDataA)

    m2 = Mesh("mesh-2")
    m2.makeMesh(fullDataB)
    """
    print("Reading Selected Polygons...")
    # Largets polygon indicates how many vertexes will be needed max for the selected landmark regions.
    selectedPolys, largestPoly = readSelectedPolygonFile(PLYPATH)
    
    for poly in selectedPolys:
        print(poly)
    
    print("Ready to compare")
    print(datetime.datetime.now())
    finalResults = []
    for i in range(len(meshes)):
        #for j in range(i, len(meshes)):
        #    if(i != j):
        #        finalResults.append([meshes[i].name + " vs " + meshes[j].name, meshes[i].compare(meshes[j],largestPoly - 3)]) # subtract 3 since that is the starting number of vertexes, and each pass adds another vertex to the generated polygons
        if(i != myObjIndex):
            finalResults.append([meshes[myObjIndex].name + " vs " + meshes[i].name, meshes[myObjIndex].compare(meshes[i], (largestPoly - 3))]) # 6 sided poly can run a full face comparison in about 15 seconds. 7 sided poly will take about a minute. output is very slow at 7 as well.
    
    for item in finalResults:
        for results in item[1]:
            print(item[0])
            print("Similar: ", results[0])
            print(len(results[0]))
            print("SemiSim: ", results[1])
            print(len(results[1]))
            print("Dis Sim: ", results[2])
            print(len(results[2]))
    
    # Check how close Noah's poly got to happening... Not changing??
    for results in finalResults[0][1]:
        if(len(results[0][0]) == 7): # 6 sided poly + 1 for similarity value
            for poly in results[0]:
                if('SN' in poly and 'MIOL' in poly and 'MIOR' in poly):
                    print(poly)
            for poly in results[1]:
                if('SN' in poly and 'MIOL' in poly and 'MIOR' in poly):
                    print(poly)
            for poly in results[2]:
                if('SN' in poly and 'MIOL' in poly and 'MIOR' in poly):
                    print(poly)
            
    selectedPolyCompares = []
            
    # Do something with Selected Polys!!
    for item in finalResults: # for each comparison result
        for results in item[1]: # for each polygon size reached
            for simList in range(len(results)): # for each list (3 lists)
                for shape in results[simList]: # for each shape in the list
                    for polygon in selectedPolys: # for each selected polygon
                        if(len(shape) - 1 == len(polygon)): # make sure the sizes are the same (-1 for similarity value)
                            vertCount = 0
                            for vertex in polygon: # for each landmark vertex in the selected polygon
                                if(vertex in shape): # check if the vertex is in the current result shape
                                    vertCount += 1
                            if(vertCount == len(shape) - 1): # if the polygon has all matching vertexes (-1 for similarity value)
                                selectedPolyCompares.append([item[0], shape, simList])
                        else:
                            pass
                   
    print(len(selectedPolyCompares))
    for item in selectedPolyCompares:
        print(item)
                
    
    #polys = []
    """
    PlotPolys = []
    for similarityList in meshes[0].compare(meshes[1], 2):
        print("Similar: ", similarityList[0])
        print("SemiSim: ", similarityList[1])
        print("Dis Sim: ", similarityList[2])
        #print(meshes[0].name, meshes[1].name)
        #polys.append(similarityList)
        PlotPolys.append(makeDrawList(allFullData[0], similarityList[0], similarityList[1], similarityList[2]))
    print(datetime.datetime.now())
    """
    """
    sideCount = 3
    for sideAmount in PlotPolys:
        plt.subplot(3,2,sideCount)
        for p in sideAmount:
            plt.plot(p[0], p[1], p[2])
            plt.title("Sides: " + str(sideCount))
        sideCount += 1
        
    for key, val in fullDataA.items():
        plt.annotate(key, xy = (val[0], val[1]))
    
    #plt.suptitle("Do Not Close this Window Until Other Window is Done") # This can (and probably will) cause the whole program to crash, but not until after the 1st OBJ is done loading...
    
    plt.show()
    """
    
if(__name__ == "__main__"):
    runCompareScript()
