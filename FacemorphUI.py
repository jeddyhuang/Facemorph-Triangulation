from tkinter import *
from tkinter import filedialog
import os
from FacemorphUINewPolygonMaker import *
from CompareJustSelected import *

class App(Tk):
    def __init__(self):
        #sets up GUI
        Tk.__init__(self)
        self.title("FaceMorph")
        
        # input stuff for Face to Compare
        Label(self, text = "Face to Compare").grid(column = 0, row = 0)
        self.basePath = Entry(self)#, text = "Path/to/File.obj")
        self.basePath.grid(column = 1, row = 0, columnspan = 2)
        self.baseBut = Button(self, text = "Select File", command = self.findBaseFile)
        self.baseBut.grid(column = 3, row = 0)
        
        # input stuff for Directory that will be searched
        Label(self, text = "Directory to Compare Against").grid(column = 0, row = 1)
        self.searchPath = Entry(self)#, text = "Path/to/Dir/")
        self.searchPath.grid(column = 1, row = 1, columnspan = 2)
        self.searchBut = Button(self, text = "Select Directory", command = self.findSearchDir)
        self.searchBut.grid(column = 3, row = 1)
        
        # input for Directory containing Selected Points files
        Label(self, text = "Directory Containing Selected Points Files").grid(column = 0, row = 2)
        self.pntPath = Entry(self)#, text = "
        self.pntPath.grid(column = 1, row = 2, columnspan = 2)
        self.pntBut = Button(self, text = "Select Directory", command = self.findPntDir)
        self.pntBut.grid(column = 3, row = 2)
        
        """
        # input stuff for Triangles file
        # This should be pre-determine, so the Face File is always the same.
        Label(self, text = "Face File").grid(column = 0, row = 3)
        self.triPath = Entry(self, text = "Path/to/triangles.txt")
        self.triPath.grid(column = 1, row = 3, columnspan = 2)
        self.triBut = Button(self, text = "Select File", command = self.findTriangleFile)
        self.triBut.grid(column = 3, row = 3)
        """
        
        # input stuff for file of Selected Polygons
        Label(self, text = "Selected Polygons File").grid(column = 0, row = 3)
        self.selPath = Entry(self, text = "Path/to/File.txt")
        self.selPath.grid(column = 1, row = 3, columnspan = 2)
        self.selBut = Button(self, text = "Find File", command = self.findSelectedPolyFile)
        self.selBut.grid(column = 3, row = 3)
        self.newTri = Button(self, text = "Make New Polygon Set", command = self.newPolys) 
        self.newTri.grid(column = 3, row = 4)
        
        Label(self, text = "Click here to overwrite the Config and start comparisons").grid(column = 0, row = 5)
        self.goBut = Button(self, text = "Start New Comparisons", command = self.begin)
        self.goBut.grid(column = 1, row = 5)
        Label(self, text = "Click here to use the current Config").grid(column = 0, row = 6)
        self.oldCFGBut = Button(self, text = "Start Comparison using old Config", command = self.beginOld)
        self.oldCFGBut.grid(column = 1, row = 6)
        
    def findBaseFile(self):
        file = filedialog.askopenfile(defaultextension = ".obj", filetypes = [('Wavefront OBJ file', '.obj')], initialdir = os.getcwd(), initialfile = "", multiple = False, parent = self)
        
        if not file is None:
            self.basePath.delete(0, END)
            self.basePath.insert(END, file.name)
            file.close()
        
        return
            
    def findSearchDir(self):
        dirname = filedialog.askdirectory(initialdir = os.getcwd(), mustexist = True)
        print(dirname)
        if(len(dirname) > 0):
            self.searchPath.delete(0, END)
            self.searchPath.insert(END, dirname)
            
        return
        
    def findPntDir(self):
        dirname = filedialog.askdirectory(initialdir = os.getcwd(), mustexist = True)
        print(dirname)
        if(len(dirname) > 0):
            self.pntPath.delete(0, END)
            self.pntPath.insert(END, dirname)
            
        return

    """
    def findTriangleFile(self):
        file = filedialog.askopenfile(defaultextension = ".txt", filetypes = [('Text File', '.txt')], initialdir = os.getcwd(), initialfile = "", multiple = False, parent = self)
        
        if not(file is None):
            self.triPath.delete(0, END)
            self.triPath.insert(END, file.name)
            file.close()
            
        return
    """
    
    def findSelectedPolyFile(self):
        file = filedialog.askopenfile(defaultextension = ".txt", filetypes = [('Text File', '.txt')], initialdir = os.getcwd(), initialfile = "", multiple = False, parent = self)
        
        if not(file is None):
            self.selPath.delete(0, END)
            self.selPath.insert(END, file.name)
            file.close()
            
        return
        
    def newPolys(self):
        # Show canvas of current triangulation(s?)
        # allow set of landmarks to be picked using left and right mouse buttons to select and deselect
        # write set into file.
        #self.newFrame = Frame
        t = Toplevel()
        w = myWindow(t)
        w.newWindow()
        
    def begin(self):
        text = ""
        text += self.basePath.get() + "\n"
        text += self.searchPath.get() + "\n"
        text += self.pntPath.get() + "\n"
        #text += self.triPath.get()
        text += self.selPath.get() + "\n"
        try:
            file = open("files.cfg", 'w')
            file.write(text)
            file.close()
            messagebox.showinfo("File Created Successfully", "The File \"files.cfg\" was created in this directory. Comparisons can now be run.")
        except:
            messagebox.showinfo("Error Writing File", "Something went wrong when writing to the output file.")
            
        # Run Compare Script.
        runCompareScript()
        
    def beginOld(self):
        runCompareScript()
        
def main():
    a = App()
    a.protocol("WM_DELETE_WINDOW", lambda: a.destroy())
    a.mainloop()
    
if __name__ == "__main__":
    main()
