import os
import shutil
import glob
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as tkmsg
import tkinter.filedialog as tkfd
import cv2
import numpy as np

#from PIL import Image
from PIL.ExifTags import TAGS

class ImageViewer():
    CANVAS_WIDTH = 530
    CANVAS_HEIGHT = 360
    #IMG_SIZE = (480,640)
    #3.1)
    def __init__(self, master):
        self.parent = master

        self.parent.bind("<Left>", self.prev)
        self.parent.bind("<Right>", self.next)

        self.init_imageviewer()

    def init_imageviewer(self):
        self.image_paths = list() # image abs_paths
        # dirs
        self.root_dir = None
        self.image_dir = None

        self.image_tk = None # showing tkimage
        self.image_idx = 0 # current image idex
        self.image_cnt = 0 # num of image
        self.image_cur_id = None # showing tkimage id

        # main frame
        self.mframe = tk.Frame(self.parent)
        self.mframe.pack(fill=tk.BOTH, expand=1)

        # image frame
        self.iframe = tk.Frame(self.mframe)
        self.iframe.pack()
        self.openImgFolderbutton = ttk.Button(self.iframe, text="Open Image Folder",  command=self.open_dir)
        self.openImgFolderbutton.pack(side = tk.TOP, padx=5)
        self.image_canvas = tk.Canvas(self.iframe, width=self.CANVAS_WIDTH, height=self.CANVAS_HEIGHT,cursor='plus')
        image_Canvas_sbarV = tk.Scrollbar(self.iframe, orient=tk.VERTICAL)
        image_Canvas_sbarH = tk.Scrollbar(self.iframe, orient=tk.HORIZONTAL)
        image_Canvas_sbarV.config(command=self.image_canvas.yview)
        image_Canvas_sbarH.config(command=self.image_canvas.xview)
        self.image_canvas.config(yscrollcommand=image_Canvas_sbarV.set)
        self.image_canvas.config(xscrollcommand=image_Canvas_sbarH.set)
        image_Canvas_sbarV.pack(side=tk.RIGHT, fill=tk.Y)
        image_Canvas_sbarH.pack(side=tk.BOTTOM, fill=tk.X)
        self.image_canvas.pack(pady=0, anchor=tk.N)

        # control frame
        self.cframe = tk.Frame(self.mframe)
        self.cframe.pack(side=tk.TOP, padx=5, pady=10)
        self.prev_button = ttk.Button(self.cframe, text="<<", width=10, command=self.prev)
        self.prev_button.pack(side = tk.LEFT, padx=5)
        self.next_button = ttk.Button(self.cframe, text=">>", width=10, command=self.next)
        self.next_button.pack(side = tk.LEFT, padx=5)

        # status frame
        self.sframe = tk.Frame(self.mframe)
        self.sframe.pack(side=tk.TOP, padx=5, pady=10)
        self.status_label = ttk.Label(self.sframe,
                                     text="{:3d}/{:3d}".format(0,0),
                                     width=10,
                                     anchor=tk.CENTER)
        self.status_label.pack(side = tk.LEFT, padx=5)
        


    #3.5)
    def prev(self, event=None):
        if self.image_cnt == 0:
            return
        if 0 < self.image_idx:
            self.image_idx -= 1
            #3.9)
            self.show_image(self.image_idx)

    #3.6)
    def next(self, event=None):
        if self.image_cnt == 0:
            return
        if self.image_idx < (self.image_cnt-1):
            self.image_idx += 1
            #3.9)
            self.show_image(self.image_idx)

    #3.8)
    def update_imagestatus(self):
        if self.image_cnt != 0:
            self.status_label.configure(text="{:3d}/{:3d}".format(self.image_idx+1,self.image_cnt))
        else:
            self.status_label.configure(text="{:3d}/{:3d}".format(0,0))

    #3.9)
    def show_image(self, idx):
        if idx < 0 or idx >= self.image_cnt:
            raise ValueError("imageidx invalid")

        self.ExactImageMetadata(self.image_paths[idx])
        #-----------------------------
        # preprocess image
        #-----------------------------
        image_cv = cv2.imread(self.image_paths[idx],cv2.IMREAD_UNCHANGED )#<class 'numpy.ndarray'>
        image_cv = cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB) # for PIL image

        image_pil = Image.fromarray(image_cv)#<class 'PIL.Image.Image'>


        w, h = image_pil.size
        disp_x = disp_y = 0
        if w>h:
            #resize fit CanvasWidth
            h = h*self.CANVAS_WIDTH/w
            w = self.CANVAS_WIDTH

        else:
            w = w*self.CANVAS_HEIGHT/h
            h = self.CANVAS_HEIGHT

        image_pil.thumbnail( (w,h) )
        self.image_tk = ImageTk.PhotoImage(image_pil) #<class 'PIL.ImageTk.PhotoImage'>

        self.image_canvas.config(scrollregion=(disp_x,disp_y, w, h))
        self.image_canvas.create_image(disp_x, disp_y, image=self.image_tk, anchor=tk.NW)

        # update status label
        #3.8)
        self.update_imagestatus()


    #3.10)
    def open_dir(self):
        # set dirs
        self.root_dir = tkfd.askdirectory()
        self.image_dir = self.root_dir

        if self.image_dir == "":
            return

        if not os.path.exists(self.image_dir):
            tkmsg.showwarning("Warning", message="{} doesn't exist.".format(self.image_dir))
            return

        if not os.path.isdir(self.image_dir):
            tkmsg.showwarning("Warning", message="{} isn't dir.".format(self.image_dir))
            return

        self.image_paths = list()
        accepted_ext = (".jpeg", '.jpg', '.png')
        for ext in accepted_ext:
            self.image_paths.extend(glob.glob(os.path.join(self.image_dir, "*"+ext)))


        image_cnt = len(self.image_paths)
        if image_cnt == 0:
            tkmsg.showwarning("Warning", message="image doesn't exist.")
            return

        self.image_idx = 0
        self.image_cnt = image_cnt
        #3.9)
        self.show_image(self.image_idx)

    def ExactImageMetadata(self, path):
        # path to the image or video
        imagename = path
        # read the image data using PIL
        image = Image.open(imagename)
        # extract EXIF data
        exifdata = image.getexif()
        #print(exifdata)
        # iterating over all EXIF data fields
        for tag_id in exifdata:
            # get the tag name, instead of human unreadable tag id
            tag = TAGS.get(tag_id, tag_id)
            data = exifdata.get(tag_id)
            # decode bytes 
            if isinstance(data, bytes):
                data = data.decode()
            print(f"{tag:25}: {data}")
#--------------------------------------------------------
# main
#--------------------------------------------------------
if __name__ == '__main__':
    root = tk.Tk()
    ImageViewer(root)
    root.resizable(width=True, height=True)
    #root.geometry(MAIN_DISPLAY_SIZE)
    root.mainloop()

