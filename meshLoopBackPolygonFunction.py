import math
import copy
import datetime

# Law of Cosides for finding an Angle.
def angle (a, b, c):
    return math.degrees(math.acos((c**2 - b**2 - a**2)/(-2.0 * a * b)))

# Simple 3D Euclidian Distance
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
    #faces = readFaceFile(TRIPATH)
    #numFaces = len(faces)
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

    def __init__(self, faces, name="mesh"):
        self.name = name
        self.verts = {}
        self.faces = faces
        self.numFaces = len(faces)
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
    # The labels will match vertexes of predetermined triangles from the Faces file (read above)
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

    # LOOK AT THIS?? Not sure it means anything?
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
    
    def makeBiggerPolygon(self, faceList, oldAngleList, constTriAngleList):
        """ LARGER POLYGON COLLECTION & COMPARISON """
        
        # Check neighboring triangles to make larger polygons.
        # Find neighboring triangle, then get angle at same vertexes on matching edge(s)
        # Add same vertex angles together and compare
        polygonList = []
        newAngleList = []
        faceCounter = 0
        #print(oldAngleList)
        for f in faceList: # Each polygon in facelist
            myNeighbors = self.getNeighbors(f)
            for tri in myNeighbors: # Each neighbor triangle
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
                        #if(len(f) > 3):
                        #    print(f)
                        #    print(oldAngleList[faceCounter])
                        #    print(f[vertex])
                        #    print(oldAngleList[faceCounter][vertex])
                        #    print(tri)
                        #    print(oldAngleList[tri[-1]])
                        #    print(constTriAngleList[tri[-1]])
                        #    print(tri.index(f[vertex]))
                        #    print(oldAngleList[tri[-1]][tri.index(f[vertex])])
                        #    print("next vert")
                        myNewAngle = constTriAngleList[tri[-1]][tri.index(f[vertex])] + oldAngleList[faceCounter][vertex] # Add angles together
                        #print(f, tri)
                        #print(myAnglesAll[faceCounter], myAnglesAll[tri[-1]])
                        if(needOtherVert):
                            newFace.append(altVert)
                            newAngles.append(constTriAngleList[tri[-1]][tri.index(altVert)])
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
                    newAngles.append(constTriAngleList[tri[-1]][tri.index(altVert)])
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
    
    # This function is used to determine polygons that loop back to an old vertex
    # The other function can only make polygons larger by absorbing a neighboring triangle's unincluded vertex
    # This function will make polygons like GOL M GOR MLS, which the above function cannot do.
    def makeLoopedPolygons(self, faceList, oldAngleList, constTriAngleList):
        #if(len(faceList[0]) > 3): # This shouldn't be the case... 
        polygonList = []
        newAngleList = []
        faceCounter = 0
        #print(oldAngleList)
        for f in faceList: # Each polygon in facelist
            myNeighbors = self.getNeighbors(f)
            neighborsWithCommonEdge = []
            i = 0
            j = 1
            while(i < len(myNeighbors)):
                while(j < len(myNeighbors)):
                    #print(set(myNeighbors[i][:-1]).intersection(set(myNeighbors[j][:-1])))
                    if(len(set(myNeighbors[i][:-1]).intersection(set(myNeighbors[j][:-1]))) == 2):
                        # need to check if pairing already in list?
                        neighborsWithCommonEdge.append([myNeighbors[i], myNeighbors[j]])
                    j += 1
                i += 1
            
            #print(neighborsWithCommonEdge)
            #print(f)
            
            # Vertex to leave will be shared by all 3: neighbor pair and current polygon.
            # vertex that needs to be added in pair is not in current polygon.
            
            for pair in neighborsWithCommonEdge:
                newLoopPoly = []
                newLoopAngles = []
                newVertex = list(set(pair[0][:-1]) - set(f))[0] # get the name of the vertex(es) that are shared by the neighbors, but not by the polygon
                skipVertex = list(set(f).intersection(set(pair[0][:-1]), set(pair[1][:-1]))) # This is the vertex that is shared by all 3. This one will be removed from the new shape. This one is left as a list for later set arithmatic
                if(len(skipVertex) > 1):
                    # if there is more than one skip vertex, that means that the 2 trianges share the same edge with the face.
                    # This could be caused by the multiple triangulations in the same file.
                    #print("Tried to loop back across different triangulations. Skipping.")
                    pass
                else:
                    updateVert0 = list(set(f).intersection(set(pair[0][:-1])) - set(skipVertex))[0] # This is the vertex shared with tri0 that is not shared with all 3
                    updateVert1 = list(set(f).intersection(set(pair[1][:-1])) - set(skipVertex))[0] # this is the vertex shared with tri1 that is not shared with all 3
                    updateVert0Angle = constTriAngleList[pair[0][-1]][pair[0].index(updateVert0)] + oldAngleList[faceCounter][f.index(updateVert0)]
                    updateVert1Angle = constTriAngleList[pair[1][-1]][pair[1].index(updateVert1)] + oldAngleList[faceCounter][f.index(updateVert1)]
                    
                    staticVert = list(set(f) - set(pair[0][:-1]) - set(pair[1][:-1])) # These are the vertexes that will not change for the new shape.
                    
                    newLoopPoly.append(updateVert0)
                    newLoopAngles.append(updateVert0Angle)
                    
                    myNewAngle = constTriAngleList[pair[0][-1]][pair[0].index(newVertex)] + constTriAngleList[pair[1][-1]][pair[1].index(newVertex)]
                    newLoopPoly.append(newVertex)
                    newLoopAngles.append(myNewAngle)
                    
                    newLoopPoly.append(updateVert1)
                    newLoopAngles.append(updateVert1Angle)
                    
                    for vertex in staticVert:
                        newLoopPoly.append(vertex)
                        newLoopAngles.append(oldAngleList[faceCounter][f.index(vertex)])
                        
                    shouldAdd = True
                    for poly in polygonList:
                        if(set(newLoopPoly) == set(poly)):
                            shouldAdd = False
                            break
                    if(shouldAdd):
                        polygonList.append(newLoopPoly)
                        newAngleList.append(newLoopAngles)
                
                    #for vertex in pair[0][:-1]:
                    #    if(vertex in pair[1]):
                            # oldAngleList[index from tri1][matching vertex] + oldAngleList[index from tri2][matching vertex]
                    #        myNewAngle = oldAngleList[pair[0][-1]][pair[0][pair[0].index(pair[0][vertex])]]
                    
            
            #print("nextFace")
            faceCounter += 1
                
        return(polygonList, newAngleList)

        
    # faceList is the Tiangulated Face file, ratioMin/MaxMatrix is the Distances between the landmarks Normalized by the Minimum/Maximum Distance,
    # myAngles are the angles of each triangle for the current mesh, other angles are the angles of each triangle for the mesh being compared,
    # comparedZAngles is a matrix of angle comparisons using the normal vector of each triangle.
    def getSimilarityValues(self, faceList, ratioMinMatrix, ratioMaxMatrix, myAngles, otherAngles, comparedZAngles):
        """ THESHOLD COMPARISONS """
        
        # These are basically arbitrary and can be fine-tuned to accept "more" or "less" similar faces
        # These values were based on their respective values as calculated using test face A and B
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
            maximumSimVal = (3 * len(f)) + usedZAngles # here, 3 is the number of metrics(Min, Max & myAngles). Zangles need to be counted in seperately, since each triangle has 1 normal
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
        
    def doLargerShapeCalls(self, otherMesh, shapeList, myShapeAngleAngles, otherShapeAngles, myAnglesAll, otherAnglesAll):
        # Get larger shapes once, to get loopable shapes.
        trash, myShapeAngleAngles = self.makeBiggerPolygon(shapeList, myShapeAngleAngles, myAnglesAll)
        shapeList, otherShapeAngles = otherMesh.makeBiggerPolygon(shapeList, otherShapeAngles, otherAnglesAll)
        #print(len(shapeList))
        #print(len(myShapeAngleAngles))
        #print(len(myAnglesAll))
        # if a set of looped shapes has already been produced (i.e. This is not the first pass)
        """
        if(len(shapeList[0]) > 3):
            # Make bigger polys from those too.
            trash, myTempShapeAngles1 = self.makeBiggerPolygon(shapeList, myShapeAngleAngles, myAnglesAll)
            tempShapeList, otherTempShapeAngles1 = otherMesh.makeBiggerPolygon(shapeList, otherShapeAngles, otherAnglesAll)
            # go thru the current shape list & check if the looped shape is already in there
            # Not sure how/when this would happen, but good to check.
            for tempShape in range(len(tempShapeList)):
                shouldAdd = True
                for shape in shapeList:
                    if(set(shape) == set(tempShapeList[tempShape])):
                        print("BiggerPoly:", shape)
                        print("LoopedPoly:", tempShapeList[tempShape])
                        shouldAdd = False
                
                if(shouldAdd):
                    shapeList.append(tempShapeList[tempShape])
                    myShapeAngleAngles.append(myTempShapeAngles[tempShape])
                    otherShapeAngles.append(otherTempShapeAngles[tempShape])
        print(len(shapeList[0]))
        # Sanity check
        for shape in shapeList:
            if(len(shape) != len(shapeList[0])):
                print("Shape in Wrong List")
                print(shape)
                print(shapeList[0])
        """
        # loop new larger shapes
        # can loop looped shapes. Should that be done? How many times?
        # Need to loop. Will loop 5 times for now. Not sure about impact. -> Impact seems to be linear. 5 loops ~ 10 sec.; 10 loops ~ 20 sec
        # looping different times doesn't seem to make the same polygons????
        for loops in range(5):
            trash, myLoopedShapeAngles = self.makeLoopedPolygons(shapeList, myShapeAngleAngles, myAnglesAll)
            loopedShapeList, otherLoopedShapeAngles = otherMesh.makeLoopedPolygons(shapeList, myShapeAngleAngles, otherAnglesAll)
            
            for i in range(len(loopedShapeList)):
                shouldAdd = True
                for shape in shapeList:
                    if(set(shape) == set(loopedShapeList[i])):
                        #print("CurrentPoly:", shape)
                        #print("LoopedPoly:", loopedShapeList[i])
                        shouldAdd = False
                if(shouldAdd):
                    shapeList.append(loopedShapeList[i])
                    myShapeAngleAngles.append(myLoopedShapeAngles[i])
                    otherShapeAngles.append(otherLoopedShapeAngles[i])
            
            #print(len(shapeList[0]))
            # Sanity check
            for shape in shapeList:
                if(len(shape) != len(shapeList[0])):
                    print("Shape in Wrong List")
                    print(shape)
                    print(shapeList[0])
        
        return(shapeList, myShapeAngleAngles, otherShapeAngles)
                
        
    
    # Compare distances as ratios to find similar facial structures
    def compare(self, otherMesh, timesToGetNeighbors = 1):
        # This is going to be the workhorse of the program.
        # Logic can be added here for any comparison, but it will all have to be done in ratios
        # We can divide each distance by the other mesh's at the same [i][j] position to get the ratios
        # from there, you can use the face list to find the shape of the triangles and shared edges
        
        """ GET COMPARE METRICS """
        
        print("Comparing " + self.name + " to " + otherMesh.name)
        print(datetime.datetime.now())
        
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
            #print(f)
            myAngles.append(angle(self.labelMatrix[f[2]][f[0]], self.labelMatrix[f[0]][f[1]], self.labelMatrix[f[1]][f[2]]))
            myAngles.append(angle(self.labelMatrix[f[0]][f[1]], self.labelMatrix[f[1]][f[2]], self.labelMatrix[f[2]][f[0]]))
            #myAngles.append(angle(self.labelMatrix[f[1]][f[2]], self.labelMatrix[f[2]][f[0]], self.labelMatrix[f[0]][f[1]]))
            myAngles.append(180.0 - myAngles[0] - myAngles[1])
            #print(myAngles)

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
        #loopedShapeList = copy.deepcopy(self.faces)
        myShapeAngleAngles = copy.deepcopy(myAnglesAll)
        otherShapeAngles = copy.deepcopy(otherAnglesAll)
        # Times to get Neighbors is how many times the shapes will be expanded.
        # getting neighbors once means that each triangle will turn into a 4-sided polygon for each neighboring vertex.
        # getting neighbors twice means that each (generated) 4-sided polygon will turn into a 5-sided polygon and so on. 
        while shapeCounter < timesToGetNeighbors:
            #print(shapeList)
            shapeList, myShapeAngleAngles, otherShapeAngles = self.doLargerShapeCalls(otherMesh, shapeList, myShapeAngleAngles, otherShapeAngles, myAnglesAll, otherAnglesAll)
            #print(shapeList)
            returnList.append([])
            returnList[-1] = copy.deepcopy(self.getSimilarityValues(shapeList, ratioMinMatrix, ratioMaxMatrix, myShapeAngleAngles, otherShapeAngles, comparedZAngles))
            shapeCounter += 1
        
        return(returnList)