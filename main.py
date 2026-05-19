import translate
import ocr
import os
import pyautogui
import tempfile
import cv2
import logging
import ctypes
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
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
duration = 100

class TemporaryError(Exception) :
    pass

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
    Label(root, text="v 1.1", font=('Arial', 10)).place(x=350,y=375)
    Label(root, text="▶ Functions", font=('Arial', 10)).place(x=10, y=70)
    Button(root, text="Edit Area", command=lambda:capGUI()).place(x=50, y=100, width=150)
    Button(root, text="ScreenShot Test", command=lambda:Screenshot_Test()).place(x=220, y=100, width=150)
    Label(root, text="▶ Options", font=('Arial', 10)).place(x=10, y=150)
    Label(root, text="Language", font=('Arial',10)).place(x=30,y=180)
    #E1 = Entry(root)
    #E1.insert(0, 'eng')
    #E1.place(x=120,y=180,width=50)
    supportlang = supportLang()[1]
    supportlangcode = supportLang()[0]
    E1 = StringVar()
    E1.set("English")
    OptionMenu(root, E1, *supportlang).place(x=30,y=210,width=175)
    #Label(root, text="to", font=('Arial', 10)).place(x=175, y=210)
    #E2 = Entry(root)
    #E2.insert(0, 'ko')
    #E2.place(x=200,y=210,width=50)
    E2 = StringVar()
    E2.set("Korean")
    translangcode=['ko', 'en', 'ja', 'zh-CN', 'zh-TW', 'es', 'fr', 'de', 'ru', 'pt', 'it', 'vi', 'th', 'id', 'hi']
    translang=['Korean', 'English', 'Japanese', 'Chinese(Simpilfied)', 'Chinese(Traditional)','Spanish', 'France', 'German', 'Russian','Pourtuguese', 'Italian', 'Vietnamese', 'Thai','Indonesian','Hindian']
    OptionMenu(root, E2, *translang).place(x=30,y=250,width=200)
    Label(root, text="Refresh Duration (ms)", font=('Arial',10)).place(x=30,y=300,width=175)
    E3 = Entry(root)
    E3.insert(0, '100')
    E3.place(x=210,y=300,width=30)
    Button(root, text="Start", command=lambda:StartUI()).place(x=25,y=330,width=250, height=30)
    Button(root, text="Stop", command=lambda:UIEnd()).place(x=280,y=330,width=95, height=30)
    Button(root, text="Apply", command=lambda:applysettings()).place(x=280,y=210,width=95, height=75)
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
    global root3
    root3.destroy()

def hide_overlay() :
    global root3
    root3.withdraw()
    show_overlay()

def show_overlay() :
    global root3,  td, path, startlang, labellist, lx, ly, rx, ry, duration
    hide_job = None
    try :
        pyautogui.screenshot(os.path.join(path, 'screen.png'),region=(lx, ly, abs(rx-lx), abs(ry-ly)))

        root3.deiconify()
        for i in labellist :
            i.destroy()
        del labellist[:]
            
        image(os.path.join(path, 'screen.png'), os.path.join(path, 'gray.png'))
        rectext = ocr.ImagetoTxt(td, os.path.join(path, 'gray.png'), langCode=startlang)[0]
        text = "\n".join(ocr.ImagetoTxt(td, os.path.join(path, 'gray.png'), langCode=startlang)[1])
        
        if len(rectext) != 0 :

            translated = translate.Trans(text, startlang, targetlang, translate.getKey()).split('\n')
            translated = list(filter(None, translated))
            
            if(len(rectext) != len(translated)) :
                raise TemporaryError()

            
            for i in range(0, len(rectext)) :
                labellist.append(Label(root3, text=translated[i], font=('Arial', 10)))
                labellist[-1].place(x=lx+rectext[i][0][0][0], y=ly+rectext[i][0][0][1])
            
        
        root3.update()
        if hide_job is not None:
            root3.after_cancel(hide_job)
        
        hide_job = root3.after(duration, lambda: hide_overlay())
        
    except TemporaryError:
        messagebox.showerror("Error", "Temporary Error Occurred. Please Try Again.")
        logging.error("Temporary Error : OCR and Translated Text Length Mismatch. OCR Result : %s, Translated Result : %s"%(rectext.replace('\n', '(newline)'), translated).replace('\n', '(newline)'))
        logging.error("%s, %s"%(len(rectext), len(translated)))
        
    except Exception as e:
        messagebox.showerror("Error", "Unknown Error Appeared. Please Check the Log : %s"%os.path.abspath('SCTransLog.log'))
        logging.error('Main Process Error : %s'% e)


def StartUI() :
    global lx, ly, rx, ry, rep, td, path, startlang, targetlang, root3, px, py, labellist
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
    labellist = list()

    root3 = Toplevel()
    root3.overrideredirect(1)
    root3.configure(bg='#ffffff')
    root3.wm_attributes('-transparentcolor','#ffffff')
    root3.attributes('-alpha',0.8)
    root3.attributes('-topmost', 'true')
    root3.geometry('1920x1080+0+0')
    hwnd = ctypes.windll.user32.GetParent(root3.winfo_id())
    
    styles = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
    styles = styles | 0x80000 | 0x20
    ctypes.windll.user32.SetWindowLongW(hwnd, -20, styles)
    
    show_overlay()

#init()
mainGUI()

#pyautogui.screenshot('foo.png',region=(0,0, 300, 400))

#print(translate.Trans('Hello World!'))