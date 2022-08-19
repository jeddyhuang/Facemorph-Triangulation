from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
import os
from FacemorphUITriangleSelect import *

class myWindow():
    def __init__(self, window):
        self.window = window
        
    def newWindow(self):
        self.window.landmarkPositions = { 'G': [400,50], 'LS': [400,390], 'GN': [400,525], 'MSOL': [250,50], 'M': [400,550], 'N': [400,150], 'MLS': [400,475], 'PG': [400,500], 
                                     'SN': [400,300], 'MIOR': [550,240], 'LI': [400,450], 'MIOL': [250,240], 'DACL': [340,190], 'GOL': [175,540], 'ZL': [25,315], 
                                     'ECTL': [100,150], 'ACPL': [325,330], 'GOR': [600,540], 'MSOR': [550,50], 'ACPR': [475,330], 'ZR': [750,315], 'DACR': [460,190], 'ECTR': [650,150] }
        self.window.selected = []
        self.window.width = 950
        self.window.height = 650
        
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
        self.window.myCanvas.bind("<Button-1>", self.mouseOne)
        self.window.myCanvas.bind("<Button-3>", self.mouseTwo)
        
        # Listbox Object
        self.window.listBox = Listbox(self.window, height = 40, width = 30, selectmode = SINGLE)
        self.window.listBox.grid(column = 4, row = 1)
        self.window.listBox.bind("<<ListboxSelect>>", self.viewSelectedPolygon)
        
        # Row 3. Clear Button, Listbox update Buttons, & Save list Button
        self.clearBut = Button(self.window, text = "Clear Points", command = self.clearSelected)
        self.clearBut.grid(column = 0, row = 2)
        
        self.window.commitBut = Button(self.window, text = "Save This Polygon", command = self.addPolygon)
        self.window.commitBut.grid(column = 1, row = 2)
        self.window.deleteBut = Button(self.window, text = "Delete Polygon from List", command = self.delPolygon)
        self.window.deleteBut.grid(column = 2, row = 2)
        
        self.window.loadBut = Button(self.window, text = "Load a List", command = self.loadPolygonFile)
        self.window.loadBut.grid(column = 4, row = 2)
        
        self.window.saveBut = Button(self.window, text = "Ready To Pick Triangles", command = self.writePolygonFile)
        self.window.saveBut.grid(column = 1, row = 3, columnspan = 2)
        
    def clearSelected(self):
        self.window.selected.clear()
        self.drawLandmarks()
        
    def addPolygon(self):
        if(len(self.window.selected) >= 3):
            # Check if polygon is already in the list
            items = self.window.listBox.get(0,END) # Get items in listbox
            shouldMake = True
            if(len(items) > 0):
                for poly in items: # Go thru the items in the listbox
                    # make sure the current listbox polygon does not have the same vertexes as the selected polygon
                    if(len(set(poly.split()) ^ set(self.window.selected)) == 0): # This is the symmetric difference of the 2 sets. It will be zero when both sets contain only the same elements.
                        shouldMake = False
                        print(poly.split())
                        print(self.window.selected)
                        messagebox.showinfo("Polygon Already in List", "The Selected Polygon already exists in the list as:\n" + poly)
                        break
            if(shouldMake):
                polyString = " ".join(self.window.selected)
                self.window.listBox.insert(END, polyString)
                self.clearSelected()
        else:
            messagebox.showinfo("Polygon Not Big Enough", "Please Make sure your selected polygon has at least 3 vertexes.")
        
    def delPolygon(self):
        selPoly = self.window.listBox.curselection()
        if(len(selPoly) != 0):
            self.window.listBox.delete(selPoly[0]) # Works since only 1 polygon can be selected at a time
        self.clearSelected()
            
    def writePolygonFile(self):
        items = self.window.listBox.get(0,END)
        t = Toplevel()
        w = myTriWindow(t)
        w.makeTriWindow(items)
        """
        print(items)
        if(len(items) > 0):
            text = ""
            for poly in items:
                if(poly not in text):
                    text += poly + "\n"
            print(text)
            try:
                file = open("NewPolygonSelection.txt", 'w')
                file.write(text)
                file.close()
                messagebox.showinfo("File Written Successfully", "The file \"NewPolygonSelection.txt\" was created in this directory.\n Clicking Save again will overwrite this file unless it is moved or renamed Manually.")
            except:
                messagebox.showinfo("Error Writing File", "Something went wrong when writing to the output file.")
        """
                
    def loadPolygonFile(self):
        messagebox.showinfo("Current List will be Overwritten", "Loading another file will clear the current list. Make sure you save your work.")
        
        file = filedialog.askopenfile(defaultextension = ".txt", filetypes = [('Selected Polygon File', '.txt')], initialdir = os.getcwd(), initialfile = "", multiple = False, parent = self.window)
        
        if(not file is None):
            text = []
            try:
                for line in file:
                    text.append(line.strip())
            except:
                messagebox.showinfo("Error Reading File", "There was an issue when reading the file.")
                return
            
            self.window.listBox.delete(0, END)
            for item in text:
                self.window.listBox.insert(END, item)
            
    
    # Left click on canvas to select landmark, click again to deselect.
    def mouseOne(self, event):
        #print(event.x, event.y)
        for key, val in self.window.landmarkPositions.items():
            if(event.x >= val[0] - 5 and event.x <= val[0] + 5):
                if(event.y >= val[1] - 5 and event.y <= val[1] + 5):
                    if(key not in self.window.selected):
                        self.window.selected.append(key)
                    else:
                        self.window.selected.remove(key)
                    self.drawLandmarks()
                    break
    
    # Right click to deselect landmark
    def mouseTwo(self, event):
        #print(event.x, event.y)
        for key, val in self.window.landmarkPositions.items():
            if(event.x >= val[0] - 5 and event.x <= val[0] + 5):
                if(event.y >= val[1] - 5 and event.y <= val[1] + 5):
                    if(key in self.window.selected):
                        self.window.selected.remove(key)
                    else:
                        pass # right click is just to remove
                        
                    self.drawLandmarks()
                    break
    
    def viewSelectedPolygon(self, event):
        w = event.widget;
        #if(len(self.window.selected) != 0):
        #    messagebox.showinfo("Items Still Selected", "Please Commit or Clear your Selections.")
        #    return
        self.window.selected.clear()
        data = w.get(w.curselection()[0]).split(" ")
        #print(data)
        for vert in data:
            self.window.selected.append(vert)
        self.drawLandmarks()
    
    # This should be used when updating selections
    def drawLandmarks(self):
        for key, value in self.window.landmarkPositions.items():
            if(key in self.window.selected):
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
            self.clearSelected()
            self.drawTriangulatiton(newTriangulation)
     
    # Only called by updateTriangulation. This will update the lines between the landmarks on screen
    def drawTriangulatiton(self, newTriScheme):
        self.window.myCanvas.delete("all")
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
                    data = newLine[0].split()
                    self.window.myCanvas.create_line(self.window.landmarkPositions[data[0]][0], self.window.landmarkPositions[data[0]][1], self.window.landmarkPositions[data[1]][0], self.window.landmarkPositions[data[1]][1])
                    self.window.myCanvas.create_line(self.window.landmarkPositions[data[1]][0], self.window.landmarkPositions[data[1]][1], self.window.landmarkPositions[data[2]][0], self.window.landmarkPositions[data[2]][1])
                    self.window.myCanvas.create_line(self.window.landmarkPositions[data[2]][0], self.window.landmarkPositions[data[2]][1], self.window.landmarkPositions[data[0]][0], self.window.landmarkPositions[data[0]][1])
            file.close()
            