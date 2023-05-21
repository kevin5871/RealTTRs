import translate
import ocr
import os
import sys
import pyautogui
import tempfile
import time
import cv2
import logging
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
import textwrap
import requests
from bs4 import BeautifulSoup

logging.basicConfig(filename='RealTTRsLog.log', level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
td = tempfile.TemporaryDirectory()
path = td.name

pos = None
lx, ly, rx, ry = None, None, None, None
px, py = None, None

startlang = 'Original Language'
targetlang = 'Translated Language'
duration = 1

def supportLang() :
    webpage = requests.get('https://www.jaided.ai/easyocr/')
    soup = BeautifulSoup(webpage.content, "html.parser")

    list1 = soup.find_all("td")
    LanguageList = list()
    LanguageCode = list()
    for i in range(0, len(list1)) :
        list1[i] = str(list1[i]).replace("<td>", "").replace("</td>", "")

    for i in range(0, len(list1)) :
        if i % 2 != 0 :
            LanguageCode.append(list1[i])
        else :
            LanguageList.append(list1[i])
    
    return  (LanguageCode, LanguageList)

def applysettings() :
    global E1, E2, E3, startlang, targetlang, duration, translangcode, translang, supportlangcode, supportlang
    # Language Options
    if E1.get() == "Original Language" :
        messagebox.showerror("Error", "Select Original Language.")
        return
    elif E2.get() == "Translated Language" :
        messagebox.showerror("Error", "Select Translated Language.")
        return
    else :
        startlang = supportlangcode[supportlang.index(E1.get())]
        targetlang = translangcode[translang.index(E2.get())]
    # Duration Options
    if type(int(E3.get())) != type(1) :
        messagebox.showerror("Error", "Duration must be Number.")
        return
    else :
        duration = int(E3.get())
    messagebox.showinfo("Success", "Settings are all applied.")



def cap_button_pressed() :
    global root1, lx, ly, rx, ry
    lx = root1.winfo_rootx()
    ly = root1.winfo_rooty()
    rx = lx+root1.winfo_width()
    ry = ly+root1.winfo_height()
    #print(lv_x, lv_y, lv_x+width, lv_y+height)
    root1.destroy()

def capGUI() :
    global root1
    root1 = Toplevel()
    root1.title("Place where you want to translate.")
    #root1.attributes('-topmost', 'true')
    root1.attributes('-alpha', 0.8)
    #root1.wm_attributes('-fullscreen','true')
    #root1.overrideredirect(1)
    root1.geometry('300x200')
    button1 = Button(root1, text="OK", command=lambda:cap_button_pressed()). place(x=10, y=10)
    Label(root1, text="Place where you want to translate.").place(x=10, y=50)
    Label(root1, text="You can resize this as well.").place(x=10, y=90)
    Label(root1, text="Press OK when done.").place(x=10, y=130)
    root1.mainloop()

def print_button_pressed() :
    global root4, px, py
    px = root4.winfo_rootx()
    py = root4.winfo_rooty()
    root4.destroy()

def printUI() :
    global root4
    root4 = Toplevel()
    root4.title("Output Management")
    #root1.attributes('-topmost', 'true')
    root4.attributes('-alpha', 0.8)
    #root1.wm_attributes('-fullscreen','true')
    #root1.overrideredirect(1)
    root4.geometry('300x200')
    Label(root4, text="(OUTPUT STARTS FROM HERE)").place(x=10,y=10)
    Label(root4, text="Place where you want to get an output").place(x=10, y=50)
    button1 = Button(root4, text="OK", command=lambda:print_button_pressed()). place(x=10, y=75)
    root4.mainloop()

def close() :
    global td, root
    td.cleanup()
    root.destroy()

def mainGUI() :
    global root, E1, E2, E3, translangcode, translang, supportlangcode, supportlang
    root = Tk()
    root.title("RealT-TRs")
    #root.attributes('-disabled', True)
    root.geometry('400x400')
    Label(root, text="RealTTRs", font=('Arial',25)).place(x=10, y=10)
    Label(root, text="v 1.0.1", font=('Arial', 10)).place(x=340,y=375)
    Label(root, text="▶ Functions", font=('Arial', 10)).place(x=10, y=70)
    Button(root, text="Edit Area", command=lambda:capGUI()).place(x=50, y=100)
    Button(root, text="ScreenShot Test", command=lambda:Screenshot_Test()).place(x=230, y=100)
    Button(root, text="Edit Print", command=lambda:printUI()).place(x=140, y=100)
    Label(root, text="▶ Options", font=('Arial', 10)).place(x=10, y=150)
    Label(root, text="Language", font=('Arial',10)).place(x=30,y=180)
    #E1 = Entry(root)
    #E1.insert(0, 'eng')
    #E1.place(x=120,y=180,width=50)
    supportlang = supportLang()[1]
    supportlangcode = supportLang()[0]
    E1 = StringVar()
    E1.set("Original Language")
    OptionMenu(root, E1, *supportlang).place(x=30,y=210,width=175)
    #Label(root, text="to", font=('Arial', 10)).place(x=175, y=210)
    #E2 = Entry(root)
    #E2.insert(0, 'ko')
    #E2.place(x=200,y=210,width=50)
    E2 = StringVar()
    E2.set("Translated Language")
    translangcode=['ko', 'en', 'ja', 'zh-CN', 'zh-TW', 'es', 'fr', 'de', 'ru', 'pt', 'it', 'vi', 'th', 'id', 'hi']
    translang=['Korean', 'English', 'Japanese', 'Chinese(Simpilfied)', 'Chinese(Traditional)','Spanish', 'France', 'German', 'Russian','Pourtuguese', 'Italian', 'Vietnamese', 'Thai','Indonesian','Hindian']
    OptionMenu(root, E2, *translang).place(x=30,y=250,width=200)
    Label(root, text="Refresh Duration (sec)", font=('Arial',10)).place(x=30,y=300,width=175)
    E3 = Entry(root)
    E3.insert(0, '1')
    E3.place(x=210,y=300,width=30)
    Button(root, text="Start", command=lambda:StartUI()).place(x=25,y=330,width=150)
    Button(root, text="Stop", command=lambda:UIEnd()).place(x=180,y=330,width=95)
    Button(root, text="Apply", command=lambda:applysettings()).place(x=280,y=330,width=95)
    root.protocol("WM_DELETE_WINDOW", close)
    root.resizable(False, False)
    root.mainloop()

def image(image, target) :
    image1 = cv2.imread(image)
    imagegray = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    imagethresh = cv2.threshold(imagegray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    #print(imagethresh, type(imagethreshE1 = Entry(top, bd =5)))
    cv2.imwrite(target,imagethresh)

def is_clicked(x, y, button, pressed):
    global pos
    if pressed:
        pos = pyautogui.position()
        return False 

def Screenshot_Test() :
    global lx, ly, rx, ry
    if lx == None and ly == None and rx == None and ry == None :
            messagebox.showerror("Error!", "You must Set Area before testing.")
            return
    pyautogui.screenshot(os.path.join(path, 'screen.png'),region=(lx, ly, abs(rx-lx), abs(ry-ly)))    
    root2 = Toplevel()
    load = Image.open(os.path.join(path, 'screen.png'))
    root2.geometry(str(load.size[0])+'x'+str(load.size[1]))
    render = ImageTk.PhotoImage(load)
    #os.system(os.path.join(path, 'screen.png'))
    img = Label(root2, image=render)
    img.image = render
    img.place(x=0,y=0)
    root2.resizable(False,False)
    #root2.mainloop()

def UIEnd() :
    global flag, root3
    flag = 0
    root3.destroy()

def StartUI() :
    global lx, ly, rx, ry, rep, td, path, startlang, targetlang, flag, root3, px, py
    if lx == None and ly == None and rx == None and ry == None :
            messagebox.showerror("Error!", "You must Set Area before start.")
            return
    if E1.get() == "Original Language" :
        messagebox.showerror("Error", "Select Original Language.")
        return
    elif E2.get() == "Translated Language" :
        messagebox.showerror("Error", "Select Translated Language.")
        return
    key = translate.getKey()
    flag = 1
    if px == None :
        px = lx
    if py == None :
        py = ly
    root3 = Toplevel()
    #print(+'x'+str(abs(ry-ly))+'+'+str(lx)+'+'+str(ly))
    root3.geometry(str(10000)+'x'+str(10000)+'+'+str(px)+'+'+str(py))
    root3.overrideredirect(1)
    root3.configure(bg='#ffffff')
    root3.attributes('-alpha',0.8)
    root3.wm_attributes('-transparentcolor','#ffffff')
    root3.attributes('-topmost', 'true')
    ocrtext = StringVar(value="OCR Text")
    transtext = StringVar(value="Translated Text")
    TransLabel = Label(root3, textvariable=transtext, font=('Arial', 20))
    TransLabel.place(x=10,y=10)
    OCRLabel = Label(root3, textvariable=ocrtext, font=('Arial', 10))
    OCRLabel.place(x=10,y=50)
    #t = threading.Thread(target=mouse)
    #t.start()
    while flag :
        try :
            root3.withdraw()

            pyautogui.screenshot(os.path.join(path, 'screen.png'),region=(lx, ly, abs(rx-lx), abs(ry-ly)))
            image(os.path.join(path, 'screen.png'), os.path.join(path, 'gray.png'))
            rectext = ocr.ImagetoTxt(td, os.path.join(path, 'gray.png'), langCode=startlang)
            if(len(rectext) == 0) :
                rectext = "(No Texts Detected.)"
            ocrtextval = rectext.replace('\n', ' | ')
            ocrtext.set(textwrap.fill(ocrtextval, width=150))
            #ocrtext.set(rectext)
            transtextval = translate.Trans(rectext, startlang, targetlang, key).replace('\n', ' | ')
            #print(len(transtextval))
            transtext.set(textwrap.fill(transtextval, width=50))
            #transtext.set(textwrap.fill(translate.Trans(rectext, startlang, targetlang, key).replace('\n', ' | ')), width=80)
            #transtext.set(translate.Trans(rectext, startlang, targetlang, key))
            root3.deiconify()
            root3.update_idletasks()
            #root3.update()
            OCRLabel.place(x=10,y=10+int(TransLabel.winfo_height()))
            root3.update_idletasks()
            root3.update()

            #t.do_run = False  
            #t.join()      
            time.sleep(duration)
        except Exception as e:
            messagebox.showerror("Error", "Unknown Error Appeared. Please Check the Log : %s"%os.path.abspath('SCTransLog.log'))
            logging.error('Main Process Error : %s'% e)
            break
    #root3.mainloop()
    #t.do_run = False  
    #t.join()

#init()
mainGUI()

#pyautogui.screenshot('foo.png',region=(0,0, 300, 400))

#print(translate.Trans('Hello World!'))