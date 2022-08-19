# Taken and Modified From: https://www.pygame.org/wiki/OBJFileLoader
# Switched some things to work with 3.6
# Removed Materials for now.

import numpy as np
import datetime
from numba import jit
import math
import sys

# I have to make my own versions of these functions because JIT does not support the numpy ones.
@jit(nopython=True)
def dotProd(u, v):
    return((u[0] * v[0]) + (u[1] * v[1]) + (u[2] * v[2]))
        
@jit(nopython=True)
def crossProd(u, v):
    x = u[1] * v[2] - u[2] * v[1]
    y = u[2] * v[0] - u[0] * v[2]
    z = u[0] * v[1] - u[1] * v[0]
    return((x, y, z))
    
@jit(nopython=True)
def normalize(v):
    magnituded = math.sqrt(dotProd(v,v))
    return((v[0] / magnituded, v[1] / magnituded, v[2] / magnituded))

# Had to seperate out the vertexes for JIT
@jit(nopython=True)
def isContained(container, containee, item0, item1, item2):#, volumes):
    # Container is the multi-sided polygon being checked (Not used?)
    # containee a vertex from a given face in the OBJ object
    # item0 is the 1st 3D vertex of the triangle being checked
    # item1 is the 2nd 3D vertex of the triangle being checked
    # item2 is the 3rd 3D vertex of the triangle being checked

    # A, B, C are the 3 vertexes that make up the triangle being checked.
    A = np.array([item0[0], item0[1], item0[2]])
    B = np.array([item1[0], item1[1], item1[2]])
    C = np.array([item2[0], item2[1], item2[2]])
    
    #print(A,B,C)
    
    AB = B - A
    AC = C - A
    
    #print(AB, AC)
    
    # AB & Normal are used to calculate the other 2D axis for the projection
    norm = np.array(crossProd(AB, AC))
    normalizedNorm = normalize(norm)
    
    normalizedAB = normalize(AB)
    orthogToNormAndAB = np.array(crossProd(AB, norm))
    normalizedOrthog = normalize(orthogToNormAndAB)
    
    #print(normalizedNorm, normalizedAB, normalizedOrthog)
    
    # origin of plane will be A
    
    P = np.array([containee[0], containee[2], containee[1]])
    
    # Barycentric Coordinates
    # Barycentric Coordinates
    # Get 2D point coords relative to A for P, B and C
    dist = dotProd(normalizedNorm, P-A)
    coorduP = dotProd(normalizedAB, P-A)
    coordvP = dotProd(normalizedOrthog, P-A)
    
    coorduB = dotProd(normalizedAB, B-A)
    coordvB = dotProd(normalizedOrthog, B-A)
    
    coorduC = dotProd(normalizedAB, C-A)
    coordvC = dotProd(normalizedOrthog, C-A)
    
    Vec2DAB = np.array([coorduB, coordvB])
    Vec2DAC = np.array([coorduC, coordvC])
    
    Vec2DAP = np.array([coorduP, coordvP])
    
    # Compute dot products
    dot00 = dotProd(Vec2DAC, Vec2DAC)
    dot01 = dotProd(Vec2DAC, Vec2DAB)
    dot02 = dotProd(Vec2DAC, Vec2DAP)
    dot11 = dotProd(Vec2DAB, Vec2DAB)
    dot12 = dotProd(Vec2DAB, Vec2DAP)
    
    # Compute barycentric coordinates
    invDenom = 1 / ((dot00 * dot11) - (dot01 * dot01))
    u = ((dot11 * dot02) - (dot01 * dot12)) * invDenom
    v = ((dot00 * dot12) - (dot01 * dot02)) * invDenom

    # Check if point is in triangle
    if((u >= 0) and (v >= 0) and (u + v < 1)):
        #print(container)
        return True
            
    return False

class OBJ:
    def __init__(self, filename, polygonSimLists, mesh, swapyz=False):
        """Loads a Wavefront OBJ file. """
        self.vertices = []
        self.normals = []
        self.texcoords = []
        self.faces = []
        
        self.name = mesh.name

        # Not using Materials for this.
        material = None
        f = open(filename, "r")
        for line in f:
            if line.startswith('#'): continue
            values = line.split()
            if not values: continue
            if values[0] == 'v':
                v = list(map(float, values[1:4]))
                if swapyz:
                    v = v[0], v[2], v[1]
                self.vertices.append(v)
            elif values[0] == 'vn':
                v = list(map(float, values[1:4]))
                if swapyz:
                    v = v[0], v[2], v[1]
                self.normals.append(v)
            elif values[0] == 'vt':
                self.texcoords.append(map(float, values[1:3]))
            # Don't need these two.
            elif values[0] in ('usemtl', 'usemat'):
                material = values[1]
            elif values[0] == 'mtllib':
                self.mtl = None
            #
            elif values[0] == 'f':
                face = []
                texcoords = []
                norms = []
                for v in values[1:]:
                    w = v.split('/')
                    face.append(int(w[0]))
                    if len(w) >= 2 and len(w[1]) > 0:
                        texcoords.append(int(w[1]))
                    else:
                        texcoords.append(0)
                    if len(w) >= 3 and len(w[2]) > 0:
                        norms.append(int(w[2]))
                    else:
                        norms.append(0)
                self.faces.append((face, norms))

        f.close()
        # this list will be compiled in doDraw in the calling script
        self.gl_list = None
        
        self.colors = [(.466,.466,.466) for i in range(len(self.vertices))]
        
        #MeshVolumes = self.makeBoundingVolumes(mesh)
        # isContained will be called len(self.faces) * len(vertices) * len(mesh.faces) times
        # Actually was getting called a lot more than that. :/ 3 times as much, i think.
        # 152,079 * 3 * 42 = 19,161,954
        # 3 for number of vertexes per face
        totalPasses = len(self.faces) * 3 * len(mesh.faces)
        passCounter = 0
        print("Starting Containment Checks")
        for f in self.faces:
            vertices, normals = f
            # Skip some faces? every other face? every 3rd face?
            
            # For each vertex, go thru the similarity lists & determine if it is contained by a polygon in that list
            for i in range(len(vertices)):
                #SimListCounter = 0
                #while SimListCounter < len(polygonSimLists): # 0th index should be the similar polygons
                for polygon in polygonSimLists[0]:
                    # Grab all viable triangles for the mesh (for larger polygons)
                    # for each triangle in the mesh, check if the new face is in that triangle
                    for face in mesh.faces:
                        # if all verts of a triangle are in the containing shape, that triangle is also in the shape.
                        if(face[0] in polygon and face[1] in polygon and face[2] in polygon):
                            # self.vertices is the actual list of vertexes from the .obj file
                            # vertecies[i] - 1 is pulled from the face list, 
                            # JIT didn't like that polygon has mismatched types & doesn't like nested lists
                            if(isContained(polygon[:-1], self.vertices[vertices[i] - 1], mesh.verts[face[0]], mesh.verts[face[1]], mesh.verts[face[2]])):#, MeshVolumes)):
                                #if(SimListCounter == 0):
                                    # Green
                                self.colors[vertices[i] - 1] = (0,1.0,0)
                                #elif(SimListCounter == 1):
                                    # Yellow
                                #    self.colors[vertices[i] - 1] = (1.0,1.0,0)
                                #elif(SimListCounter == 2):
                                    # Red
                                #    self.colors[vertices[i] - 1] = (1.0,0,0)
                                break
                    passCounter += 1
                    # This is doing weird stuff after removing While loop. Just remove? Change to timer?
                    if(passCounter % 1000000 == 0):
                        print(datetime.datetime.now())
                        print(mesh.name, " Pass Counter: ", passCounter, " of (maximum) ", totalPasses)
                        #sys.stdout.flush()
                    #SimListCounter += 1
                    
        print(datetime.datetime.now())
        print(mesh.name, " Pass Counter: ", passCounter, " of ", totalPasses)
