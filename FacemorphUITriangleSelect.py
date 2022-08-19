from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
import os

class myTriWindow():
    def __init__(self, triWindow):
        self.window = triWindow
        
    def makeTriWindow(self, polygonList):
        #print(polygonList)
        self.window.receivedList = polygonList
        self.window.landmarkPositions = { 'G': [400,50], 'LS': [400,390], 'GN': [400,525], 'MSOL': [250,50], 'M': [400,550], 'N': [400,150], 'MLS': [400,475], 'PG': [400,500], 
                                     'SN': [400,300], 'MIOR': [550,240], 'LI': [400,450], 'MIOL': [250,240], 'DACL': [340,190], 'GOL': [175,540], 'ZL': [25,315], 
                                     'ECTL': [100,150], 'ACPL': [325,330], 'GOR': [600,540], 'MSOR': [550,50], 'ACPR': [475,330], 'ZR': [750,315], 'DACR': [460,190], 'ECTR': [650,150] }
        self.window.curPoly = 0
        self.window.selected = []
        self.window.curPolyVerts = []
        self.window.width = 950
        self.window.height = 650
        
        self.window.polys = []
        self.window.clickablePolys = []
        self.window.triTagList = {}
        self.window.finalTriangles = {}
        
        # Top row. Triangulation Selector & Update button for Triangulation Selector
        Label(self.window, text = "Select Triangulation").grid(column = 0, row = 0)
        optionList = ("default", "Alt Cheek", "New Nose", "Alt Nose") # If you add a new triangulation, you must add an option here, and update drawTriangulatiton
        self.window.curTriValue = StringVar()
        self.window.curTriValue.set(optionList[0])
        self.window.oldTriangulation = optionList[0]
        self.window.dropdown = OptionMenu(self.window, self.window.curTriValue, *optionList)
        self.window.dropdown.grid(column = 1, row = 0)
        self.window.updateBut = Button(self.window, text = "Update", command = self.updateTriangulation)
        self.window.updateBut.grid(column = 2, row = 0)
        
        # Canvas object
        self.window.myCanvas = Canvas(self.window, height = 600, width = 800, bg = "white")
        self.window.myCanvas.grid(column = 0, row = 1, columnspan = 3)
        self.drawTriangulatiton(self.window.oldTriangulation)
        
        # Label to show current polygon
        self.window.myLabel = StringVar()
        self.window.triLabel = Label(self.window, textvariable=self.window.myLabel)
        self.window.triLabel.grid(column = 4, row = 0)
        
        # Listbox Object
        self.window.listBox = Listbox(self.window, height = 40, width = 30, selectmode = SINGLE)
        self.window.listBox.grid(column = 4, row = 1)
        self.window.listBox.bind("<<ListboxSelect>>", self.viewSelectedPolygon) # change to highlight triangle?
        
        # Row 3. Clear Button, Listbox update Buttons, & Save list Button
        self.clearBut = Button(self.window, text = "Clear Triangles", command = self.clearSelected)
        self.clearBut.grid(column = 0, row = 2)
        
        self.window.prevBut = Button(self.window, text = "Previous Polygon", command = self.prevPolygon)
        self.window.prevBut.grid(column = 1, row = 2)
        
        self.window.commitBut = Button(self.window, text = "Save this Polygon", command = self.finalizeSelection)
        self.window.commitBut.grid(column = 2, row = 2)
        
        self.window.nextBut = Button(self.window, text = "Next Polygon", command = self.nextPolygon)
        self.window.nextBut.grid(column = 3, row = 2)
        
        self.window.saveBut = Button(self.window, text = "All Polygons Made", command = self.writePolygonFile)
        self.window.saveBut.grid(column = 1, row = 3, columnspan = 2)
        
        for item in self.window.receivedList:
            self.window.listBox.insert(END, item)
        
        self.updateLabel()
        self.setUpPolys()
        
        
    def clearSelected(self):
        self.window.selected.clear()
        for poly in self.window.clickablePolys:
            self.window.myCanvas.itemconfig(poly, fill = '')
        self.drawLandmarks()
        
    def prevPolygon(self):
        if(self.window.curPoly > 0):
            self.window.curPoly -= 1
            self.clearSelected()
            self.updateLabel()
            
        
    def nextPolygon(self):
        if(self.window.curPoly < len(self.window.receivedList) - 1):
            self.window.curPoly += 1
            self.clearSelected()
            self.updateLabel()
            
    def updateLabel(self):
        self.window.curPolyVerts.clear()
        labelStr = self.window.receivedList[self.window.curPoly]
        self.window.myLabel.set(labelStr)
        verts = labelStr.split(" ")
        for v in verts:
            self.window.curPolyVerts.append(v)
        self.window.listBox.selection_clear(0,END)
        self.window.listBox.select_set(self.window.curPoly)
        self.updateSelection()
        self.drawLandmarks()
        
    def updateSelection(self):
        # load selected triangles if available.
        found = False
        lb = self.window.listBox
        if(lb.get(lb.curselection()[0]) in self.window.finalTriangles): # check selection in final list
            #print("In Final list")
            for tri in self.window.finalTriangles[lb.get(lb.curselection()[0])]: # check final list triangles
                for key, value in self.window.triTagList.items(): # check tag list 
                    #print(tri, value)
                    if(tri == value): # if triangle in final list matches the current tagged triangle
                        for poly in self.window.clickablePolys: # check clickable triangles
                            tag = self.window.myCanvas.gettags(poly)[0] # get tag of each clickable triangle
                            #print(key, int(tag))
                            if(key == int(tag)): # if clickable tag matches the current checked tag
                                #print("found!!")
                                self.window.myCanvas.itemconfig(poly, fill='red') # update that triangle
                                self.window.selected.append(tag)
                                found = True
                                break
        
    def finalizeSelection(self):
        polygon = self.window.receivedList[self.window.curPoly]
        if(polygon not in self.window.finalTriangles): # if new polygon
            self.window.finalTriangles[polygon] = []
        else: # if polygon already exists.
            self.window.finalTriangles[polygon].clear() # Redo in case edits made to selection.
            
        for canvasItemID in self.window.selected:
            #for key, value in self.window.triTagList.items():
            tag = int(self.window.myCanvas.gettags(canvasItemID)[0]) # returned as array with 1 item
            # if current polygon already in final list
            self.window.finalTriangles[polygon].append(self.window.triTagList[tag])
        print(self.window.finalTriangles)
            
    def writePolygonFile(self):
        try:
            file = open("SelectedTriangleList.txt", "w")
            for key, value in self.window.finalTriangles.items():
                file.write(key)
                file.write(":")
                for tri in value:
                    file.write(tri)
                    file.write("-")
                file.write("\n")
            file.close()
            messagebox.showinfo("File Written Successfully", "The file \"SelectedTriangleList.txt\" was created in this directory.\n Clicking Save again will overwrite this file unless it is moved or renamed Manually.")
        except:
            messagebox.showinfo("Error Writing File", "Something went wrong when writing to the output file.")
                    
    
    # Left click on canvas to select landmark, click again to deselect.
    def mouseOne(self, event):
        obj = event.widget.find_closest(event.x, event.y)
        if(obj[0] not in self.window.selected):
        #if(self.window.myCanvas.itemcget(obj[0], 'fill') == ''):
            self.window.myCanvas.itemconfig(obj[0], fill='red')
            self.window.selected.append(obj[0])
        else:
            self.window.myCanvas.itemconfig(obj[0], fill='')
            self.window.selected.remove(obj[0])
            
        self.drawTriangulatiton(self.window.oldTriangulation)
        
    
    # Right click to deselect landmark
    def mouseTwo(self, event):
        obj = event.widget.find_closest(event.x, event.y)
        if(obj[0] in self.window.selected):
        #if(self.window.myCanvas.itemcget(obj[0], 'fill') == 'red'):
            self.window.myCanvas.itemconfig(obj[0], fill='')
            self.window.selected.remove(obj[0])
        self.drawTriangulatiton(self.window.oldTriangulation)
    
    # NEED TO UPDATE THIS
    def viewSelectedPolygon(self, event):
        w = event.widget;
        #if(len(self.window.selected) != 0):
        #    messagebox.showinfo("Items Still Selected", "Please Commit or Clear your Selections.")
        #    return
        self.window.curPolyVerts.clear()
        self.clearSelected()
        #print(w.curselection())
        #print(w.curselection()[0])
        data = w.get(w.curselection()[0]).split(" ")
        self.window.curPoly = w.curselection()[0]
        self.updateLabel()
    
    # This should be used when updating selections
    def drawLandmarks(self):
        for key, value in self.window.landmarkPositions.items():
            if(key in self.window.curPolyVerts):
                self.window.myCanvas.create_oval(value[0] - 5, value[1] - 5, value[0] + 5, value[1] + 5, fill = "red")
            else:
                self.window.myCanvas.create_oval(value[0] - 5, value[1] - 5, value[0] + 5, value[1] + 5, fill = "blue")
            self.window.myCanvas.create_text(value[0] + 10, value[1], anchor = W, text = key, font = "Helvetica 18")
     
    # This is used when updating Triangulations
    def updateTriangulation(self):
        #if(len(self.window.selected) != 0):
        #    messagebox.showinfo("Items Still Selected", "Please Commit or Clear your Selections.")
        #    return
        newTriangulation = self.window.curTriValue.get()
        if(newTriangulation != self.window.oldTriangulation):
            self.window.oldTriangulation = newTriangulation
            self.window.myCanvas.delete("all")
            self.drawTriangulatiton(newTriangulation)
            self.clearSelected()
            self.setUpPolys()
            
    def setUpPolys(self): # how to get selected triangles back??
        tagCounter = 0
        for poly in self.window.polys:
            # reverse engineer polygon
            # The bad part about seperating drawing from set up...
            #print(poly)
            vert1 = [poly[0], poly[1]]
            vert2 = [poly[2], poly[3]]
            vert3 = [poly[4], poly[5]]
            translatedPoly = []
            for key, value in self.window.landmarkPositions.items():
                if value[0] == vert1[0] and value[1] == vert1[1]:
                    translatedPoly.append(key)
                elif value[0] == vert2[0] and value[1] == vert2[1]:
                    translatedPoly.append(key)
                elif value[0] == vert3[0] and value[1] == vert3[1]:
                    translatedPoly.append(key)
            #print(translatedPoly)
            translatedKey = " ".join(translatedPoly)
            self.window.triTagList[tagCounter] = translatedKey # can now bee used to associate click events with correct triangle.
            
            nextPoly = self.window.myCanvas.create_polygon(poly, tags=str(tagCounter), fill='', width=1)
            self.window.clickablePolys.append(nextPoly)
            self.window.myCanvas.tag_bind(self.window.clickablePolys[-1], "<Button-1>", self.mouseOne)
            self.window.myCanvas.tag_bind(self.window.clickablePolys[-1], "<Button-3>", self.mouseTwo)
            tagCounter += 1
            
        #print(self.window.triTagList)
     
    # This will update the lines between the landmarks on screen
    def drawTriangulatiton(self, newTriScheme):
        self.drawLandmarks()
        
        path = ""
        
        # Adding triangulations will require an update here.
        if(newTriScheme == "default"):
            path = ".\\TriangulationDefault.txt"
        elif(newTriScheme == "Alt Cheek"):
            path = ".\\TriangulationCheekAlt.txt"
        elif(newTriScheme == "New Nose"):
            path = ".\\TriangulationNewNose.txt"
        elif(newTriScheme == "Alt Nose"):
            path = ".\\TriangulationNoseAlt.txt"
        else:
            messagebox.showinfo("Something Went Wrong", "There was an error getting the Triangulation File. Please check that the files are intact and not renamed.")
            
        if(path != ""):
            file = open(path, 'r')
            for line in file:
                newLine = line.split("#") # Allow for comments in Triangulation files.
                if newLine[0] != "":
                    # Add newline to some sort of list?
                    data = newLine[0].split()
                    # skip lines and just draw polygons?
                    self.window.myCanvas.create_line(self.window.landmarkPositions[data[0]][0], self.window.landmarkPositions[data[0]][1], self.window.landmarkPositions[data[1]][0], self.window.landmarkPositions[data[1]][1])
                    self.window.myCanvas.create_line(self.window.landmarkPositions[data[1]][0], self.window.landmarkPositions[data[1]][1], self.window.landmarkPositions[data[2]][0], self.window.landmarkPositions[data[2]][1])
                    self.window.myCanvas.create_line(self.window.landmarkPositions[data[2]][0], self.window.landmarkPositions[data[2]][1], self.window.landmarkPositions[data[0]][0], self.window.landmarkPositions[data[0]][1])
                    
                    self.window.polys.append([]) # add list to put points for next polygon
                    self.window.polys[-1].append(self.window.landmarkPositions[data[0]][0]) # x0
                    self.window.polys[-1].append(self.window.landmarkPositions[data[0]][1]) # y0
                    self.window.polys[-1].append(self.window.landmarkPositions[data[1]][0]) # x1
                    self.window.polys[-1].append(self.window.landmarkPositions[data[1]][1]) # y1
                    self.window.polys[-1].append(self.window.landmarkPositions[data[2]][0]) # x2
                    self.window.polys[-1].append(self.window.landmarkPositions[data[2]][1]) # y2
                    # create_polygon will wrap back to x0,y0 for me
                    # use tags when creating polygons for easy click events
                    
            file.close()
        #self.setUpPolys()
        
