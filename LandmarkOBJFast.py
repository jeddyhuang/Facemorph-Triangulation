import numpy as np
import matplotlib.pyplot as plt
import linecache
import math
import copy
import datetime
import threading
import multiprocessing as mp

import sys, pygame
from pygame.locals import *
from pygame.constants import *
from OpenGL.GL import *
from OpenGL.GLU import *

# IMPORT OBJECT LOADER
from OBJLoaderFastEarlyExit import *

FirstFace = "A"
SecondFace = "B"

# Reads the pos files provided
def readObjFile(FaceLetter):
    fullData = {}
    # Selected Point is the index list of the Landmark Points in the obj File
    # Get the Vertexes from the Obj File
    SelectedPath = ".\\TestData\\Selected Points\\" + FaceLetter + ".TXT"
    objPath = ".\\TestData\\Together\\" + FaceLetter + "\\" + FaceLetter + ".obj"
    print(objPath)
    SelectedFile = open(SelectedPath, 'r')
    #ObjectFile = open(objPath, 'r')
    for line in SelectedFile:
        index = line.split()
        #print(index)
        data = linecache.getline(objPath, int(index[1]) + 1).split()
        #print(data)
        fullData[index[0]] = [float(data[1]), float(data[2]), float(data[3][:-1])] # Remove Newline char from end of z data
    SelectedFile.close()
    #objFile.close()
    return(fullData)

# Expects a file where the Landmark Point names are listed 3 on a line, seperated by spaces.
def readFaceFile(path):
    faceData = []
    file = open(path, 'r')
    for line in file:
        data = line.split()
        faceData.append(data)

    file.close
    #print(faceData)
    return faceData

def makeNPArray(fullData):
    formattedData = []
    for key,val in fullData.items():
        formattedData.append(val)
    data = np.array(formattedData)
    #print(data)
    return(data)
    
# Law of Cosides for finding an Angle.
def angle (a, b, c):
    return math.degrees(math.acos((c**2 - b**2 - a**2)/(-2.0 * a * b)))

def calcDist(x1, y1, z1, x2, y2, z2):
    #print(x1, y1, x2, y2)
    xSqd = pow((x2 - x1), 2)
    ySqd = pow((y2 - y1), 2)
    zSqd = pow((z2 - z1), 2)
    #print(xSqd, ySqd)
    return(math.sqrt(xSqd + ySqd + zSqd))
    # Below for printing. Screen too small.
    #return(round(math.sqrt(xSqd + ySqd), 2))

# The mesh object that holds information about the face in question.
# This could probably be moved to it's own file. 
class Mesh():
    name = "mesh"
    # faces contains the labels of the 3 points. these are used for dictionary lookups in Verts
    #   `-> [GOL, MG, G] 
    faces = readFaceFile(r".\MyTriangles.txt")
    numFaces = len(faces)
    #FullData is already labeled Vertexes
    # verts is a dictionary that uses the graph label as an "index"
    #   `-> {GOL : [x, y]}
    numVerts = 0
    verts = {}
    # label matrix is a dict of dicts that allow nested key lookups
    # This means labelMatrix[GOL][G] = dist from GOL to G
    #   `-> {GOL : {GOL : 0, G : 153.5, ...}, G: {...}, ...}
    labelMatrix = {}
    # These have the same structure as labelMatrix
    # To normalize the data, I divide each distance by the minimum
    minDist = 9999
    NormalizedMinDists = {}
    # To normalize the data, divide each dist by max dist to get all dists as a percentage of the max, to allow for meaningful comparisons
    maxDist = 0
    NormalizedMaxDists = {}
    # ZAngles will be a dict where the 3 points used to make the angle will be the key and the angle between them will be the value
    ZAngles = {}

    def __init__(self, name="mesh"):
        self.name = name
        self.verts = {}
        self.labelMatrix = {}
        self.NormalizedMinDists = {}
        self.minDist = 9999
        self.NormalizedMaxDists = {}
        self.maxDist = 0
        self.ZAngles = {}

    # Makes a copy of full data into this Mesh Object & preps needed Matrixes
    def makeMesh(self, fullData):
        for key,val in fullData.items():
            self.verts[key] = val
        self.calcDists()
        #print(self.minDist)
        #print(self.maxDist)
        #print("MIN:")
        self.minNormalize()
        #print("MAX:")
        self.maxNormalize()
        self.getZAngles()

    # Populates the distance matrix using the labels as lookup values
    # The labels will match predetermined triangles from the Faces file (read above)
    def calcDists(self):
        pointCount = len(self.verts)
        # Make Matrix to hold dists
        self.labelMatrix = {}
        
        for key in self.verts.keys():
            self.labelMatrix[key] = {}
            for innerKey in self.verts.keys():
                self.labelMatrix[key][innerKey] = 0
        
        # For each triangle defined in the Face file
        # This can be abstracted to allow for shapes other than triangles (since 3 is hard coded)
        #   `-> To do this, change the 3's to len(f)
        for f in self.faces:
            counter = 0
            # for each vertex of the face
            while counter < 3:
                # if the distance between the 2 vertexes has not been calculated yet
                i = f[counter]
                j = f[(counter + 1) % 3]
                # and condition might be redundant??
                if (self.labelMatrix[i][j] == 0) and (self.labelMatrix[j][i] == 0):
                    A = []
                    B = []
                    A = self.verts[i]
                    B = self.verts[j]
                    #print(A, B)
                    dist = calcDist(A[0], A[1], A[2], B[0], B[1], B[2])
                    self.labelMatrix[i][j] = dist
                    self.labelMatrix[j][i] = dist
                    # Update Normalization Distances
                    if dist < self.minDist:
                        self.minDist = dist
                    if dist > self.maxDist:
                        self.maxDist = dist
                    #print(labelMatrix[i][j])
                counter += 1

        #print("DISTS:")
        #self.printLabelMatrix()

    def minNormalize(self):
        # Have to copy like this to avoid reference vs. value issues
        self.NormalizedMinDists = copy.deepcopy(self.labelMatrix)

        for key in self.labelMatrix.keys():
            for innerKey in self.labelMatrix.keys():
                self.NormalizedMinDists[key][innerKey] = self.NormalizedMinDists[key][innerKey] / self.minDist
            #print(self.NormalizedMinDists[key])
        
    def maxNormalize(self):
        self.NormalizedMaxDists = copy.deepcopy(self.labelMatrix)

        for key in self.labelMatrix.keys():
            for innerKey in self.labelMatrix.keys():
                self.NormalizedMaxDists[key][innerKey] = self.NormalizedMaxDists[key][innerKey] / self.maxDist
            #print(self.NormalizedMaxDists[key])

    def printLabelMatrix(self):
        for key, val in self.labelMatrix.items():
            print(key, ":", val)
            
    def getZAngles(self):
        # For each face, get the neighboring face and find the angle between the Normal Vectors of those 2 planes
        for face in self.faces:
            myVert1 = self.verts[face[0]]
            myVert2 = self.verts[face[1]]
            myVert3 = self.verts[face[2]]
            
            myA = [myVert1[0] - myVert2[0], myVert1[1] - myVert2[1], myVert1[2] - myVert2[2]]
            myB = [myVert3[0] - myVert2[0], myVert3[1] - myVert2[1], myVert3[2] - myVert2[2]]
            
            myCrossProdX = myA[1] * myB[2] - myA[2] * myB[1]
            myCrossProdY = myA[2] * myB[0] - myA[0] * myB[2]
            myCrossProdZ = myA[0] * myB[1] - myA[1] * myB[0]
            
            myLen = math.sqrt(pow(myCrossProdX, 2) + pow(myCrossProdY, 2) + pow(myCrossProdZ, 2))
            
            for neighborFace in self.faces:
                # If there are 2 matching points in the 2 faces
                if(len(set(face).intersection(set(neighborFace))) == 2):
                    keyStr = " ".join(face) + " x " + " ".join(neighborFace)
                    altKeyStr = " ".join(neighborFace) + " x " + " ".join(face)
                    # Check if Angle dif is already calculated.
                    if(keyStr not in self.ZAngles and altKeyStr not in self.ZAngles):
                        Vert1 = self.verts[neighborFace[0]]
                        Vert2 = self.verts[neighborFace[1]]
                        Vert3 = self.verts[neighborFace[2]]

                        a = [Vert1[0] - Vert2[0], Vert1[1] - Vert2[1], Vert1[2] - Vert2[2]]
                        b = [Vert3[0] - Vert2[0], Vert3[1] - Vert2[1], Vert3[2] - Vert2[2]]

                        CrossProdX = a[1] * b[2] - a[2] * b[1]
                        CrossProdY = a[2] * b[0] - a[0] * b[2]
                        CrossProdZ = a[0] * b[1] - a[1] * b[0]
                        
                        otherLen = math.sqrt(pow(CrossProdX, 2) + pow(CrossProdY, 2) + pow(CrossProdZ, 2))
                        
                        dotProd = (myCrossProdX * CrossProdX + myCrossProdY * CrossProdY + myCrossProdZ * CrossProdZ)
                        
                        zAngle = math.acos(dotProd / (myLen * otherLen))
                        #print(keyStr, zAngle)
                        self.ZAngles[keyStr] = zAngle

    # Returns a list of faces that share an edge
    def getNeighbors(self, face):
        neighbors = []
        index = 0        # Used to make accessing Angles easier
        for f in self.faces:
            # Don't add triangle in shape
            if(f[0] in face and f[1] in face and f[2] in face):
                pass
            else:
                vertCount = 0
                while vertCount < len(face):
                    if(face[vertCount] in f and face[(vertCount + 1) % len(face)] in f):
                        neighbors.append([f[0], f[1], f[2], index]) # Add the next triangle
                    vertCount += 1
            index += 1
        return neighbors
        
    def makeBiggerPolygon(self, faceList, oldAngleList):
        """ LARGER POLYGON COLLECTION & COMPARISON """
        
        # Check neighboring triangles to make larger polygons.
        # Find neighboring triangle, then get angle at same vertexes on matching edge(s)
        # Add same vertex angles together and compare
        # Stop finding neighboring triangles when a dissimilar shape is found?
        polygonList = []
        newAngleList = []
        faceCounter = 0
        for f in faceList: # Each face
            myNeighbors = self.getNeighbors(f)
            for tri in myNeighbors: # Each neighbor
                newFace = []
                needOtherVert = False
                newAngles = []
                altVert = [v for v in tri if v not in f][0] # Get vert from tri that is not shared
                #print(tri)
                #print(f)
                #print(altVert)
                for vertex in range(len(f)): # Each vertex of f
                    #print(f[vertex])
                    if(f[vertex] in tri): # If vertex matches any vertex in neighbor
                        myNewAngle = oldAngleList[tri[-1]][tri.index(f[vertex])] + oldAngleList[faceCounter][vertex] # Add angles together
                        #print(f, tri)
                        #print(myAnglesAll[faceCounter], myAnglesAll[tri[-1]])
                        if(needOtherVert):
                            newFace.append(altVert)
                            newAngles.append(oldAngleList[tri[-1]][tri.index(altVert)])
                            needOtherVert = False
                        newFace.append(f[vertex])
                        newAngles.append(myNewAngle)
                        needOtherVert = True
                    else:
                        needOtherVert = False
                        newFace.append(f[vertex])
                        newAngles.append(oldAngleList[faceCounter][vertex])
                if(altVert not in newFace):
                    newFace.append(altVert)
                    newAngles.append(oldAngleList[tri[-1]][tri.index(altVert)])
                #print(newFace)
                #print(newAngles)
                # Dont add the same polygon multiple times.
                shouldAdd = True
                for poly in polygonList:
                    if(set(newFace) == set(poly)):
                        shouldAdd = False
                        break
                if(shouldAdd):
                    polygonList.append(newFace)
                    newAngleList.append(newAngles)
            faceCounter += 1

        #print(polygonList)
        return(polygonList, newAngleList)
        
    def getSimilarityValues(self, faceList, ratioMinMatrix, ratioMaxMatrix, myAngles, otherAngles, comparedZAngles):
        """ THESHOLD COMPARISONS """
        
        # Using 2/3 of these averages for thresh holds. Can be changed later
        # These are arbitrary and can be fine-tuned to accept "more" or "less" similar faces
        simMinThresh = 1.33
        simMaxThresh = .02         # This value means a 2 percent difference. Good Value?
        simAngleThresh = 3.33
        simZAngleThresh = .07

        # Use face list and ratioMatrix to find similar triangles
        similarTri = []
        semiSimTri = []
        disSimTri = []

        faceCounter = 0
        for f in faceList:
            # check max for similar percentages on each side
            # check min for the same thing?
            # check dists to get idea of shape?
            counter = 0
            # Similarity Value can be up to number of measures * number Vertexes in Shape
            # Need to divide it by len(f) to get # of measures that are similar in the shape. 
            simVal = 0
            usedZAngles = 0 # How many z angles are in the shape.
            while(counter < len(f)):
                i = f[counter]
                j = f[(counter + 1) % len(f)]
                k = f[(counter + 2) % len(f)]
                if(abs(ratioMinMatrix[i][j]) <= simMinThresh):
                    simVal += 1
                if(abs(ratioMaxMatrix[i][j]) <= simMaxThresh):
                    simVal += 1
                if(abs(myAngles[faceCounter][counter] - otherAngles[faceCounter][counter]) <= simAngleThresh):
                    simVal += 1
                zAngleKeyF = " ".join((i, j, k))
                zAngleKeyB = " ".join((k, j, i))
                if(zAngleKeyF in comparedZAngles):
                    #print(zAngleKeyF)
                    if(abs(comparedZAngles[zAngleKeyF]) <= simZAngleThresh):
                        simVal += 1
                    usedZAngles += 1
                elif(zAngleKeyB in comparedZAngles):
                    #print(zAngleKeyB)
                    if(abs(comparedZAngles[zAngleKeyB]) <= simZAngleThresh):
                        simVal += 1
                    usedZAngles += 1
                # Other Comparisons
                counter += 1
            
            # Need to adjust acceptance based on size of the polygon
            maximumSimVal = (3 * len(f)) + usedZAngles # here, 3 is the number of metrics. Zangles need to be counted in seperately
            #print(maximumSimVal)
            # Larger polygons may have a different number to zAngles
            # if the similarity value is above 2/3 of the maximum
            # Playing with > vs >= can help fine tune matches.
            if(simVal >= ((2/3) * maximumSimVal)):
                newTri = f.copy()
                newTri.append(simVal)
                similarTri.append(newTri)
            # if SimVal is above 1/3 of the max
            elif(simVal >= ((1/3) * maximumSimVal)):
                newTri = f.copy()
                newTri.append(simVal)
                semiSimTri.append(newTri)
            else:
                newTri = f.copy()
                newTri.append(simVal)
                disSimTri.append(newTri)
            faceCounter += 1
            
        
        return(similarTri, semiSimTri, disSimTri)
    
    # Compare distances as ratios to find similar facial structures
    def compare(self, otherMesh, timesToGetNeighbors = 1):
        # This is going to be the workhorse of the program.
        # Logic can be added here for any comparison, but it will all have to be done in ratios
        # We can divide each distance by the other mesh's at the same [i][j] position to get the ratios
        # from there, you can use the face list to find the shape of the triangles and shared edges
        
        """ GET COMPARE METRICS """
        
        ratioMatrix = {}
        ratioMinMatrix = {}
        ratioMaxMatrix = {}
        for key in self.verts.keys():
            ratioMatrix[key] = {}
            ratioMinMatrix[key] = {}
            ratioMaxMatrix[key] = {}
            for innerKey in self.verts.keys():
                # Skip Zeros in Matrixes, since they will be zero in both
                if(self.labelMatrix[key][innerKey] != 0):
                    ratioMatrix[key][innerKey] = self.labelMatrix[key][innerKey] / otherMesh.labelMatrix[key][innerKey]
                    # Compare min & max Normalized Values
                    # Compared via subtraction to tell how much larger or smaller one edge of a triangle is than another.
                    ratioMinMatrix[key][innerKey] = self.NormalizedMinDists[key][innerKey] - otherMesh.NormalizedMinDists[key][innerKey]
                    ratioMaxMatrix[key][innerKey] = self.NormalizedMaxDists[key][innerKey] - otherMesh.NormalizedMaxDists[key][innerKey]
                else:
                    ratioMatrix[key][innerKey] = 0
                    ratioMinMatrix[key][innerKey] = 0
                    ratioMaxMatrix[key][innerKey] = 0
        
        myAnglesAll = []
        otherAnglesAll = []
        for f in self.faces:
            myAngles = []
            otherAngles = []
            # These are the sides across from the vertex at index 0, 1, 2 respectively
            # The angle of each vertex is then calculated in the same order as they appear in f
            #   `-> angle[0] is the angle of f[0] in the current triangle
            #   `-> This allows the two to be looped through together
            #   `-> The order the sides fed into the angle function was manually matched. (I made sure the vertex/angle order matched)
            #   `-> Not sure, but this may require the points to be listed in CLOCKWISE order?
            myAngles.append(angle(self.labelMatrix[f[2]][f[0]], self.labelMatrix[f[0]][f[1]], self.labelMatrix[f[1]][f[2]]))
            myAngles.append(angle(self.labelMatrix[f[0]][f[1]], self.labelMatrix[f[1]][f[2]], self.labelMatrix[f[2]][f[0]]))
            #myAngles.append(angle(self.labelMatrix[f[1]][f[2]], self.labelMatrix[f[2]][f[0]], self.labelMatrix[f[0]][f[1]]))
            myAngles.append(180.0 - myAngles[0] - myAngles[1])

            otherAngles.append(angle(otherMesh.labelMatrix[f[2]][f[0]], otherMesh.labelMatrix[f[0]][f[1]], otherMesh.labelMatrix[f[1]][f[2]]))
            otherAngles.append(angle(otherMesh.labelMatrix[f[0]][f[1]], otherMesh.labelMatrix[f[1]][f[2]], otherMesh.labelMatrix[f[2]][f[0]]))
            #otherAngles.append(angle(otherMesh.labelMatrix[f[1]][f[2]], otherMesh.labelMatrix[f[2]][f[0]], otherMesh.labelMatrix[f[0]][f[1]]))
            otherAngles.append(180.0 - otherAngles[0] - otherAngles[1])

            myAnglesAll.append(myAngles)
            otherAnglesAll.append(otherAngles)
            
        # Can just directly compare angles?
        comparedZAngles = {}
        for key in self.ZAngles.keys():
            if(key in otherMesh.ZAngles):
                comparedZAngles[key] = otherMesh.ZAngles[key] - self.ZAngles[key]

        returnList = []
        returnList.append([])
        returnList[-1] = self.getSimilarityValues(self.faces, ratioMinMatrix, ratioMaxMatrix, myAnglesAll, otherAnglesAll, comparedZAngles)
        
        # When looking at larger polygons, only the angles change. 
        # Ration Min, Max and ZAngles stay the same
        
        shapeCounter = 0
        shapeList = copy.deepcopy(self.faces)
        myShapeAngleAngles = copy.deepcopy(myAnglesAll)
        otherShapeAngles = copy.deepcopy(otherAnglesAll)
        while shapeCounter < timesToGetNeighbors:
            trash, myShapeAngleAngles = self.makeBiggerPolygon(shapeList, myShapeAngleAngles)
            shapeList, otherShapeAngles = otherMesh.makeBiggerPolygon(shapeList, otherShapeAngles)
            returnList.append([])
            returnList[-1] = copy.deepcopy(self.getSimilarityValues(shapeList, ratioMinMatrix, ratioMaxMatrix, myShapeAngleAngles, otherShapeAngles, comparedZAngles))
            shapeCounter += 1
        
        return(returnList)

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

# Objs is a list of OBJ objects from the loader
# Meshes is the list of meshes used. These are expected to be in the same order as the OBJs
# Should only be 2 OBJS.
def doDraw(objs, meshes):
    # The A Model's Y and Z are flipped
    # This was set by the swapyz param in the OBJ constructor
    # this will visually aline the Landmarks with the model
    
    # Compile Draw lists. This will make the actual drawing faster'
    print("Compiling Draw Lists")
    objs[0].gl_list = glGenLists(1)
    glNewList(objs[0].gl_list, GL_COMPILE)
    for face in objs[0].faces:
        vertices, normals = face
        glBegin(GL_POLYGON)
        for i in range(len(vertices)):
            if normals[i] > 0:
                glNormal3fv(objs[0].normals[normals[i] - 1])
            glColor3fv(objs[0].colors[vertices[i] - 1])
            glVertex3fv(objs[0].vertices[vertices[i] - 1])
        glEnd()
    glEndList()
    
    objs[1].gl_list = glGenLists(1)
    glNewList(objs[1].gl_list, GL_COMPILE)
    for face in objs[1].faces:
        vertices, normals = face
        glBegin(GL_POLYGON)
        for i in range(len(vertices)):
            if normals[i] > 0:
                glNormal3fv(objs[1].normals[normals[i] - 1])
            glColor3fv(objs[1].colors[vertices[i] - 1])
            glVertex3fv(objs[1].vertices[vertices[i] - 1])
        glEnd()
    glEndList()
    
    print("Entering Draw Loop")
    
    clock = pygame.time.Clock()
    rx, ry, rz = (90, 180, 0)
    alty = 0
    tx, ty = (0,0) #(150,0)
    zpos = 200
    rotate = False
    keepGoing = True
    while keepGoing:
        clock.tick(30)
        for e in pygame.event.get():
            if e.type == QUIT:
                keepGoing = False
            elif e.type == KEYDOWN and e.key == K_ESCAPE:
                keepGoing = False
            elif e.type == MOUSEBUTTONDOWN:
                if e.button == 4: zpos = max(1, zpos-1)
                elif e.button == 5: zpos += 1
                elif e.button == 1: rotate = True
            elif e.type == MOUSEBUTTONUP:
                if e.button == 1:
                    rotate = False
                    print(rx, ry, rz)
            elif e.type == MOUSEMOTION:
                i, j = e.rel
                if rotate:
                    if(rz + i < 90 and rz + i > -90):
                        rz += i
                        alty += i
                    if(rx + j < 180 and rx + j > 0):
                        rx += j

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)
        glEnable(GL_COLOR_MATERIAL)
        glFrontFace(GL_CCW)
        glLoadIdentity()

        # RENDER OBJECTS
        glPushMatrix()
        glTranslate(tx - 100, ty, -zpos)
        glRotate(rx, 1, 0, 0)
        glRotate(ry, 0, 1, 0)
        glRotate(rz, 0, 0, 1)
        glCallList(objs[0].gl_list)
        glPopMatrix()
        glColor3fv((1.0,0.0,0.0))
        for vertex in meshes[0].verts.values():
            glPushMatrix()
            glTranslate(tx - 100, ty, -zpos)
            glRotate(rx - 90, 1, 0, 0)
            glRotate(alty, 0, 1, 0)
            #glRotate(rz, 0, 0, 1)
            glTranslatef(-vertex[0],vertex[1],vertex[2])
            quad = gluNewQuadric()
            gluSphere(quad,5,50,10)
            glPopMatrix()
            
        
        glPushMatrix()
        glTranslate(tx + 100, ty, -zpos)
        glRotate(rx, 1, 0, 0)
        glRotate(ry, 0, 1, 0)
        glRotate(rz, 0, 0, 1)
        glCallList(objs[1].gl_list)
        glPopMatrix()
        glColor3fv((1.0,0.0,0.0))
        for vertex in meshes[1].verts.values():
            glPushMatrix()
            glTranslate(tx + 100, ty, -zpos)
            glRotate(rx - 90, 1, 0, 0)
            glRotate(alty, 0, 1, 0)
            #glRotate(rz, 0, 0, 1)
            glTranslatef(-vertex[0],vertex[1],vertex[2])
            quad = gluNewQuadric()
            gluSphere(quad,5,50,10)
            glPopMatrix()
        

        pygame.display.flip()
        
def makeObj(path, polygonSimList, mesh, outQueue):
    obj = OBJ(path, polygonSimList, mesh, swapyz=True)
    outQueue.put(obj)
    print("done")
    #outQueue.task_done()
  
def doPygame(meshes, polygonSimList):
    pygame.init()
    viewport = (1000,600)
    hx = viewport[0]/2
    hy = viewport[1]/2
    srf = pygame.display.set_mode(viewport, OPENGL | DOUBLEBUF)

    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHTING)
    glEnable(GL_DEPTH_TEST)
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.0, 0.0, 0.0, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (1.0, 1.0, 1.0, 1.0))
    glLightfv(GL_LIGHT0, GL_POSITION, (0, 0, 200, 0.0))

    glShadeModel(GL_SMOOTH)           # most obj files expect to be smooth-shaded

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    width, height = viewport
    gluPerspective(90.0, width/float(height), 1, 1000.0)
    # How to fix angles caused by perspective camera?
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_MODELVIEW)

    # LOAD OBJECT AFTER PYGAME INIT & Similarity has been determined.
    # Need OPENGL stuff to compile the list for drawing.
    print("Loading OBJS will take time. Please Wait.")
    print("Loading OBJ 1...")

    objs = []
    q = mp.Queue()
    print(polygonSimList[0]) # pass in larger polygons?
    # ~~This will take about 20 minutes~~
    # Removed while loop, so only similar regions are checked. Now runs in under 5 minutes???
    # Almost seems like this is getting run twice?
    try:
        t = mp.Process(target=makeObj, args=(".\\TestData\\Together\\" + FirstFace + "\\" + FirstFace + ".obj", polygonSimList[0], meshes[0], q))
        #obj = OBJ(".\\TestData\\Together\\" + FirstFace + "\\" + FirstFace + ".obj", polygonSimList[0], meshes[0], swapyz=True)
        t.start()
    except Exception as e:
        print("Error while loading OBJ 1")
        print(e)
        #pygame.quit()
        #sys.exit()
    print(datetime.datetime.now())
    
    print("Loading OBJ 2...")
    try:
        t2 = mp.Process(target=makeObj, args=(".\\TestData\\Together\\" + SecondFace + "\\" + SecondFace + ".obj", polygonSimList[0], meshes[1], q))
        #obj2 = OBJ(".\\TestData\\Together\\" + SecondFace + "\\" + SecondFace + ".obj", polygonSimList[0], meshes[1], swapyz=True)
        t2.start()
    except Exception as e:
        print("Error while loading OBJ 2")
        print(e)
        #pygame.quit()
        #sys.exit()
        
    
    while len(objs) != 2:
        try:
            item = q.get()
            objs.append(item)
        except q.empty():
            pass
            
    t.join()
    t2.join()
    
    print(datetime.datetime.now())
    print("Ready to Draw")
    
    myMeshes = []
    if objs[0].name == meshes[0].name:
        myMeshes.append(meshes[0])
        myMeshes.append(meshes[1])
    elif objs[0].name == meshes[1].name:
        myMeshes.append(meshes[1])
        myMeshes.append(meshes[0])
    else:
        print("error determining order of completion")
        print(len(objs))
    
    doDraw(objs, myMeshes)

    pygame.quit()

def main():
    print(datetime.datetime.now())
    # FROM MAIN
    print("Ready to Read File for Mesh Comparison")
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

    print("Making Mesh Objects")
    m = Mesh("mesh-1")
    m.makeMesh(fullDataA)

    m2 = Mesh("mesh-2")
    m2.makeMesh(fullDataB)
    print("Ready to compare")
    polys = []
    PlotPolys = []
    for similarityList in m.compare(m2, 2):
        print("Similar: ", similarityList[0])
        print("SemiSim: ", similarityList[1])
        print("Dis Sim: ", similarityList[2])
        polys.append(similarityList)
        PlotPolys.append(makeDrawList(fullDataA, similarityList[0], similarityList[1], similarityList[2]))
    print(datetime.datetime.now())

    # show 2D plot first. This will hopefully help the user understand what is going on when the 3D versions are drawn
    sideCount = 3
    for sideAmount in PlotPolys:
        plt.subplot(3,2,sideCount)
        for p in sideAmount:
            plt.plot(p[0], p[1], p[2])
            plt.title("Sides: " + str(sideCount))
        sideCount += 1
        
    for key, val in fullDataA.items():
        plt.annotate(key, xy = (val[0], val[1]))

    # plt.show is blocking...
    #plt.ion()
    
    plt.suptitle("Do Not Close this Window Until Other Window is Done") # This can (and probably will) cause the whole program to crash, but not until after the 1st OBJ is done loading...
    
    t = threading.Thread(target=doPygame, args=([m, m2], polys))
    #doPygame([m], polys)
    t.start()
    
    plt.show()
    
    t.join() # Added This before meeting with Noah and Jerry Doesn't seem to change anything. Maybe make t a mp.Process?

    #plt.draw()
    #plt.pause(0.001)
    # END OF MAIN STUFF
    
    
    
if(__name__ == "__main__"):
    main()
