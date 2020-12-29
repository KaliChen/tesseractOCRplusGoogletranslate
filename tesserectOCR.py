import platform
import cv2
import glob
import os
import numpy as np
from googletrans import Translator
import pytesseract
import tkinter as tk
from tkinter.ttk import *
#from tkinter import messagebox as msg
from tkinter.ttk import Notebook
from tkinter import ttk
import tkinter.messagebox as tkmsg
from tkinter.colorchooser import *
from PIL import Image, ImageTk, ImageDraw, ExifTags, ImageColor,ImageFont
from tkinter import filedialog
from ImgViewer.imgview import ImageViewer

fontlinetype_Item = {cv2.LINE_AA:'LINE_AA',cv2.LINE_8:'LINE_8'}
fontsize = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16, 20, 22, 24, 28, 32, 36, 40, 44, 48, 52, 54, 60, 72)
linewidth = ( 1, 2, 3, 4, 5)
font_Item = ('Arial', #normal
             'msgothic', #jpn
             'arabtype', #ara
             'mingliu',  #CN_TR
             'simsun',   #CN_Sim
             'malgun')   #ko

fontlinetype_Item = {cv2.LINE_AA:'LINE_AA',cv2.LINE_8:'LINE_8'}

class tesserectOCR():
    def __init__(self, master):
        self.parent = master
        self.color_1 = (0,0,0)
        self.color_2 = (0,0,0)
        self.imageFile = str()
        self.tesserectOCRPanel = tk.LabelFrame(self.parent, text="tesserect OCR",font=('Courier', 10))
        self.tesserectOCRPanel.pack(side=tk.TOP)
        self.init_imgview_tab()
        self.init_tesserect_tab()
        self.init_setting_tab()
        self.init_Font_tab()
        self.init_GoogleTran_tab()
        self.init_DisplaySceneMarkInfo_tab()

    def init_imgview_tab(self):
        self.imgview_tab = tk.Frame(self.tesserectOCRPanel)
        self.imgview_tab.pack(side = tk.LEFT, expand=tk.YES, fill=tk.BOTH)
        self.imgview = ImageViewer(self.tesserectOCRPanel)
        ImageConfig_Button = tk.Button(self.tesserectOCRPanel, text = "ImageConfig",font=('Courier', 8), command = self.image_config)
        ImageConfig_Button.pack(side=tk.LEFT, expand=tk.YES, fill = tk.X)

    def image_config(self, event = None):
        imageFile = self.imgview.image_paths[self.imgview.image_idx]
        self.imageFile = str(imageFile)
        self.DisplaySceneMarkInfo.insert(tk.END,self.imageFile)

    def tesseract_OCR(self, event = None):
        #self.imageFile = self.imgswitch()
        detectText = []
        print(self.imageFile)
        #if self.tesseract_OCR_langType.get() == 'eng':
        self.OCR = pytesseract.image_to_string(Image.open(self.imageFile), lang = self.tesseract_OCR_langType.get() )
        self.DisplaySceneMarkInfo.insert(tk.END,self.OCR)
        #self.DisplaySceneMarkInfo.insert(tk.END,pytesseract.image_to_boxes(Image.open(imageFile), lang = 'eng'))
        detectText = pytesseract.image_to_boxes(Image.open(self.imageFile), lang = self.tesseract_OCR_langType.get() ).splitlines()

        img = cv2.imread(self.imageFile)

        H, W, _ = img.shape
        for word in detectText:
            word_rectangle = word.split()
            x =int(word_rectangle[1])
            y =int(word_rectangle[2])
            w =int(word_rectangle[3])
            h =int(word_rectangle[4])
            imgOut = cv2.rectangle(img,(x,H-y),(w,H-h),self.color_1,int(self.linesizespinbox.get()))
            #cv2.putText(imgOut, word_rectangle[0], (x, H-y), int(self.fontcv2spinbox.get()),0.8, (0, 0, 0), 1, int(self.fontlinetypecv2spinbox.get()))
        
        # 將 NumPy 陣列轉為 PIL 影像
        imgPil = Image.fromarray(imgOut)

        # 在圖片上加入文字
        draw = ImageDraw.Draw(imgPil)
        for word in detectText:
            word_rectangle = word.split()
            x =int(word_rectangle[1])
            y =int(word_rectangle[2])
            w =int(word_rectangle[3])
            h =int(word_rectangle[4])
            draw.text((x, H-y),word_rectangle[0], font=self.font, fill = self.color_2)
        # 將 PIL 影像轉回 NumPy 陣列
        imgOut = np.array(imgPil)
        
        while True:
            # 顯示結果
            cv2.imshow("Output", imgOut)
            # 讀取使用者所按下的鍵
            k = cv2.waitKey(0) & 0xFF
            # 若按下 q 鍵，則離開
            if k == 113:
                break
            # 關閉圖形顯示視窗
        cv2.destroyAllWindows()

    def init_tesserect_tab(self):
        self.tesserect_tab = tk.Frame(self.tesserectOCRPanel)
        self.tesserect_tab.pack(side = tk.TOP, expand=tk.YES, fill=tk.BOTH)
        #self.OCR_Function.add(self.tesserect_tab, text="tesserect")
        self.tesseract_OCR_langType = ttk.Combobox(self.tesserect_tab,font=('Courier', 10),width = 25, values = ["eng","chi_tra","chi_sim","jpn","tur","ara","kir","afr", "pus", "rus"], state = "readonly") 
        self.tesseract_OCR_langType.pack(side=tk.LEFT, expand=tk.NO, fill=tk.BOTH)
        self.tesseract_OCR_langType.current(0)

        self.tesseract_OCR_Button = tk.Button(self.tesserect_tab, text = "tesseract",font=('Courier', 10), command = self.tesseract_OCR)
        self.tesseract_OCR_Button.pack(side=tk.LEFT, expand=tk.NO, fill = tk.X)

    def googleTrans(self, event = None):

        translator = Translator(service_urls=['translate.google.com',
                                              'translate.google.co.kr',
                                              'translate.google.com.tw',
                                              'translate.google.co.jp'
                                              ]
                                )
        #if self.dest_langType.get()=='en':
        translations = translator.translate([self.OCR,], dest=self.dest_langType.get())
        for translation in translations:
            #print(translation.origin, ' -> ', translation.text)
            self.DisplaySceneMarkInfo.insert(tk.END,translation.text)

    def init_GoogleTran_tab(self):
        self.GoogleTran_tab = tk.Frame(self.tesserectOCRPanel)
        self.GoogleTran_tab.pack(side = tk.TOP, expand=tk.YES, fill=tk.BOTH)
        #self.Transnotebook.add(self.GoogleTran_tab, text = "Google Translate")

        self.googleTrans_Button = tk.Button(self.GoogleTran_tab, text = "Google Translate",font=('Courier', 10), command = self.googleTrans)
        self.googleTrans_Button.pack(side=tk.LEFT, expand=tk.NO, fill = tk.X)

        self.dest_langType = ttk.Combobox(self.GoogleTran_tab,font=('Courier', 10),width = 25, values = ["en","zh-CN","ja","ko","ar"], state = "readonly") 
        self.dest_langType.pack(side=tk.LEFT, expand=tk.NO, fill = tk.X)
        self.dest_langType.current(0)

    def Select_font(self, event = None):
        for item in self.Table_of_font.selection():
            self.item_text = self.Table_of_font.item(item, "values")
            #print(self.item_text)
            #print(item)
            #print(self.item_text[0].rstrip('.ttf'))
            
            # 載入字體
        self.font = ImageFont.truetype(self.item_text[0], 20)
        tkmsg.showinfo("Information",self.item_text[0])
        ##self.font = ImageFont.truetype('arial', 20)
        ##tkmsg.showinfo("Information",'arial')

    def List_font(self, event = None):
        if platform.system() == "Windows":
            fontlist = font_Item
            """
            font_Item = ('Arial', #normal
             'msgothic', #jpn
             'arabtype', #ara
             'mingliu',  #CN_TR
             'simsun',   #CN_Sim
             'malgun')   #ko

            """
            for ttf in fontlist:
                self.Table_of_font.insert("", index = 'end', text = ttf,  values = (ttf))

        else:
            fontlist = glob.glob( "font/*.[tT][tT][fF]" )            
            for ttf in fontlist:
                (head, filename) = os.path.split(ttf)
                self.Table_of_font.insert("", index = 'end', text = filename,  values = (ttf))
        #tkmsg.showinfo("Information","Here are font types!")

    def init_Font_tab(self):
        self.Font_tab = tk.Frame(self.tesserectOCRPanel)
        self.Font_tab.pack(side = tk.TOP, expand=tk.YES, fill=tk.BOTH)
        #self.settingnotebook.add(self.Font_tab, text = "Font")

        ListFont = tk.Label(self.Font_tab)
        ListFont.pack(side=tk.TOP, expand=tk.NO)

        #self.Table_of_font = ttk.Treeview(self.Font_Setting_tab,columns = ["#1"],height = 10)
        self.Table_of_font = ttk.Treeview(ListFont,height = 3)
        self.Table_of_font.heading("#0", text = "List of font")#icon column
        #self.Table_of_font.heading("#1", text = "Path")
        self.Table_of_font.column("#0", width = 500)#icon column
        #self.Table_of_font.column("#1", width = 90)
        self.Table_of_font.tag_configure('T', font = 'Courier,4')
        self.Table_of_font.bind("<Double-1>",self.Select_font)
        self.Table_of_font.pack(side=tk.TOP, expand=tk.NO, fill=tk.BOTH)
        self.List_font_Button = tk.Button(ListFont, text = "List font",font=('Courier', 10), command = self.List_font)
        self.List_font_Button.pack(side=tk.TOP, expand=tk.YES, fill = tk.BOTH) 

    def init_setting_tab(self):
        self.setting_tab = tk.Frame(self.tesserectOCRPanel)
        self.setting_tab.pack(side = tk.TOP, expand=tk.YES, fill=tk.BOTH)
        #self.settingnotebook.add(self.ColorDraw_tab, text = "Color&Draw")

        self.MarkSettingPanel = tk.LabelFrame(self.setting_tab, text="Color and font Setting Panel",font=('Courier', 10))
        self.MarkSettingPanel.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)

        '''Color Panel'''
        ColorPanel = tk.Frame(self.MarkSettingPanel)
        ColorPanel.grid(row = 0, column = 0 ,sticky = tk.E+tk.W)        
        self.Color1Button = tk.Button(ColorPanel, text = "Color 1",font=('Courier', 10), command = self.askcolor1)
        self.Color1Button.grid(row = 0, column = 0, sticky = tk.E+tk.W)

        self.Color2Button = tk.Button(ColorPanel, text = "Color 2",font=('Courier', 10), command = self.askcolor2)
        self.Color2Button.grid(row = 1, column = 0, sticky = tk.E+tk.W)

        '''font line type setting'''
        fontcv2Panel = tk.Frame(self.MarkSettingPanel)
        fontcv2Panel.grid(row = 0, column = 1 ,sticky = tk.E+tk.W)

        '''Line Size'''
        tk.Label(self.MarkSettingPanel, text = "Line size",font=('Courier', 10)).grid(row = 0, column = 4, sticky = tk.E+tk.W)        
        #self.linesizespinbox = tk.Spinbox(self.MarkSettingPanel, from_ = 1, to = 10, increment = 1, width = 3)
        self.linesizespinbox = tk.Spinbox(self.MarkSettingPanel, values = linewidth,  width = 3)
        self.linesizespinbox.grid(row = 0, column = 5, sticky = tk.E+tk.W)

        '''font line type setting'''
        fontlinetypecv2Panel = tk.Frame(self.MarkSettingPanel)
        fontlinetypecv2Panel.grid(row = 0, column = 6 ,sticky = tk.E+tk.W)
        '''line type label'''
        tk.Label(fontlinetypecv2Panel, text = "line type",font=('Courier', 10)).pack(side = tk.TOP, expand=tk.YES, fill=tk.BOTH)       
        self.fontlinetypecv2Var = tk.IntVar()
        self.fontlinetypecv2Var.set(8)
        for val, linetype, in fontlinetype_Item.items(): 
            tk.Radiobutton(fontlinetypecv2Panel, text = linetype, variable = self.fontlinetypecv2Var, value = val,font=('Courier', 10)).pack(side = tk.TOP, expand=tk.YES, fill=tk.BOTH)
    def askcolor1(self, event = None):
        self.color1 = askcolor()
        self.Color1Button.configure(bg=self.color1[1])
        self.color_1 = self.HTMLColorToBGR(self.color1[1])

    def askcolor2(self, event = None):
        self.color2 = askcolor()
        self.Color2Button.configure(bg=self.color2[1])
        self.color_2 = self.HTMLColorToBGR(self.color2[1])

    def HTMLColorToBGR(self,colorstring):
        """ convert #RRGGBB to an (B, G, R) tuple """
        colorstring = colorstring.strip()
        if colorstring[0] == '#': colorstring = colorstring[1:]
        if len(colorstring) != 6:
            raise(ValueError, "input #%s is not in #RRGGBB format" % colorstring)
        r, g, b = colorstring[:2], colorstring[2:4], colorstring[4:]
        r, g, b = [int(n, 16) for n in (r, g, b)]
        return (b, g, r)

    def HTMLColorToRGB(self,colorstring):
        """ convert #RRGGBB to an (R, G, B) tuple """
        colorstring = colorstring.strip()
        if colorstring[0] == '#': colorstring = colorstring[1:]
        if len(colorstring) != 6:
            raise(ValueError, "input #%s is not in #RRGGBB format" % colorstring)
        r, g, b = colorstring[:2], colorstring[2:4], colorstring[4:]
        r, g, b = [int(n, 16) for n in (r, g, b)]
        return (r, g, b)

    def init_DisplaySceneMarkInfo_tab(self):
        self.DisplaySceneMarkInfo_Frame = tk.LabelFrame(self.tesserectOCRPanel, text="Display tesseract OCR and Translation Info", font=('Courier', 9))
        self.DisplaySceneMarkInfo_Frame .pack(side=tk.TOP, expand=tk.NO)
        self.DisplaySceneMarkInfo = tk.Text(self.DisplaySceneMarkInfo_Frame, width = 70, height = 7) 
        DisplaySceneMarkInfo_sbarV = Scrollbar(self.DisplaySceneMarkInfo_Frame, orient=tk.VERTICAL)
        DisplaySceneMarkInfo_sbarH = Scrollbar(self.DisplaySceneMarkInfo_Frame, orient=tk.HORIZONTAL)
        DisplaySceneMarkInfo_sbarV.config(command=self.DisplaySceneMarkInfo.yview)
        DisplaySceneMarkInfo_sbarH.config(command=self.DisplaySceneMarkInfo.xview)
        self.DisplaySceneMarkInfo.config(yscrollcommand=DisplaySceneMarkInfo_sbarV.set)
        self.DisplaySceneMarkInfo.config(xscrollcommand=DisplaySceneMarkInfo_sbarH.set)
        DisplaySceneMarkInfo_sbarV.pack(side=tk.RIGHT, fill=tk.Y)
        DisplaySceneMarkInfo_sbarH.pack(side=tk.BOTTOM, fill=tk.X)
        self.DisplaySceneMarkInfo.pack(side=tk.TOP, expand=tk.NO)
        DisplaySceneMarkInfoCLEAR =tk.Button(self.tesserectOCRPanel, text = "Clear",font=('Courier', 9), command = self.DisplaySceneMarkInfoCLEAR)
        DisplaySceneMarkInfoCLEAR.pack(side=tk.TOP, expand=tk.NO)

    def DisplaySceneMarkInfoCLEAR(self, event = None):
        self.DisplaySceneMarkInfo.delete('1.0', tk.END)
        tkmsg.showinfo("Information","CLEAR")



if __name__ == '__main__':
    root = tk.Tk()
    tesserectOCR(root)
    #tesserectOCR.imageFile = filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("jpg files","*.jpg"),("jpeg files","*.jpeg"),("all files","*.*")))
    #print(tesserectOCR.imageFile)
    #root.resizable(width=True, height=True)
    #root.geometry(MAIN_DISPLAY_SIZE)
    root.mainloop()

