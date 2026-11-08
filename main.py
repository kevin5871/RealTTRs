import translate
import ocr
import os
import pyautogui
import tempfile
import cv2
import logging
import ctypes
import time
import numpy
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
import requests
from bs4 import BeautifulSoup


logging.basicConfig(
    filename="RealTTRsLog.log",
    level=logging.INFO,
    format=(
        "%(asctime)s - %(name)s - "
        "%(levelname)s - %(message)s"
    ),
    encoding="utf-8",
    errors="backslashreplace"
)

td = tempfile.TemporaryDirectory()
path = td.name

pos = None
lx, ly, rx, ry = None, None, None, None
px, py = None, None

startlang = 'Original Language'
targetlang = 'Translated Language'
duration = 150

overlay_running = False
overlay_after_id = None

previous_frame = None
CHANGE_THRESHOLD = 3.0 # 민감도

WDA_EXCLUDE_FROM_CAPTURE = 0x00000011

def exclude_window_from_capture(window):
    window.update_idletasks()
    
    hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
    if not hwnd:
        hwnd = window.winfo_id()
        
    result = ctypes.windll.user32.SetWindowDisplayAffinity(hwnd, WDA_EXCLUDE_FROM_CAPTURE)
    if not result:
        logging.warning("Failed to set window display affinity. Error code: %d", ctypes.windll.kernel32.GetLastError())
    
    return bool(result)


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
    UIEnd()
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
    cv2.imwrite(target,imagethresh)


def has_screen_changed(current_frame):
    global previous_frame

    if previous_frame is None:
        previous_frame = current_frame.copy()
        return True, 0.0

    if previous_frame.shape != current_frame.shape:
        previous_frame = current_frame.copy()
        return True, 0.0

    diff = cv2.absdiff(previous_frame, current_frame)

    # 평균 픽셀 차이
    score = float(numpy.mean(diff))

    if score > CHANGE_THRESHOLD:
        previous_frame = current_frame.copy()
        return True, score

    return False, score


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


def UIEnd():
    global overlay_running, overlay_after_id
    global previous_frame

    # 먼저 반복 실행 중단
    overlay_running = False

    # 예약된 콜백 취소
    if overlay_after_id is not None:
        try:
            root.after_cancel(overlay_after_id)
        except TclError:
            pass

        overlay_after_id = None

    previous_frame = None

    # 오버레이 창 제거
    if "root3" in globals():
        try:
            if root3.winfo_exists():
                root3.destroy()
        except TclError:
            pass

    logging.info("Overlay stopped")


def hide_overlay() :
    global root3
    if root3.winfo_exists():
        show_overlay()




def schedule_next_capture():
    global overlay_after_id

    if not overlay_running:
        return

    if not root3.winfo_exists():
        return

    # 중복 예약 방지
    if overlay_after_id is not None:
        return

    overlay_after_id = root3.after(
        max(150, duration),
        capture_loop
    )


def capture_loop():
    global overlay_after_id

    overlay_after_id = None

    if not overlay_running:
        return

    try:
        show_overlay()

    except Exception:
        logging.exception(
            "Capture loop error"
        )

    finally:
        if overlay_running:
            schedule_next_capture()



def show_overlay():
    global root3, td, path
    global startlang, targetlang, labellist
    global lx, ly, rx, ry
    global overlay_running

    if not overlay_running:
        return

    if not root3.winfo_exists():
        return

    start_total = time.perf_counter()

    try:
        screenshot = pyautogui.screenshot(region=(lx, ly, abs(rx - lx), abs(ry - ly)))
        frame = cv2.cvtColor(numpy.array(screenshot), cv2.COLOR_RGB2GRAY)

        changed, score = has_screen_changed(frame)

        if not changed:
            logging.info(
                "Screen unchanged (%.2f), OCR skipped",
                score
            )
            return

        logging.info(
            "Screen changed: %.2f",
            score
        )

        gray = cv2.threshold(frame, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        
        gray_path = os.path.join(path, "gray.png")

        if not cv2.imwrite(gray_path, gray):
            raise RuntimeError(
                "Failed to save OCR image"
            )

        rectext, texts = ocr.ImagetoTxt(
            td,
            gray_path,
            langCode=startlang
        )
        logging.info("OCR raw texts: %r", texts)
        
        if not rectext:
            for label in labellist: label.destroy()
            labellist.clear()

            logging.info(
                "No text detected, overlay cleared"
            )
            return

        translated_text = translate.Trans(
            "\n".join(texts),
            startlang,
            targetlang
        )

        logging.info(
            "Translation raw: %r",
            translated_text
        )

        translated = translated_text.split("\n")

        if len(rectext) != len(translated):
            logging.warning(
                "OCR count (%d) != Translation count (%d)",
                len(rectext),
                len(translated)
            )

            return

        for label in labellist: label.destroy()
        labellist.clear()

        for i, item in enumerate(rectext):
            x, y = lx + int(item[0][0][0]), ly + int(item[0][0][1])
            label = Label(root3, text=translated[i], font=("Arial", 10))
            label.place(x=x, y=y)
            labellist.append(label)

        elapsed = (time.perf_counter() - start_total) * 1000

        logging.info(
            "Total processing: %.2f ms",
            elapsed
        )

    except Exception:
        logging.exception(
            "Overlay processing error"
        )





def StartUI():
    global root3, labellist, previous_frame
    global overlay_running, overlay_after_id
    global lx, ly, rx, ry

    # 중복 실행 방지
    if overlay_running:
        logging.info("Overlay is already running")
        return

    # 캡처 영역 확인
    if None in (lx, ly, rx, ry):
        messagebox.showerror(
            "Error",
            "You must Set Area before start."
        )
        return

    if rx <= lx or ry <= ly:
        messagebox.showerror(
            "Error",
            "Invalid capture area."
        )
        return

    # 언어 설정 확인
    if startlang == "Original Language":
        messagebox.showerror(
            "Error",
            "Apply language settings first."
        )
        return

    if targetlang == "Translated Language":
        messagebox.showerror(
            "Error",
            "Apply language settings first."
        )
        return

    previous_frame = None
    overlay_after_id = None
    labellist = []

    # 오버레이 창 생성
    root3 = Toplevel(root)
    root3.overrideredirect(True)
    root3.configure(bg="#ffffff")
    root3.wm_attributes(
        "-transparentcolor", "#ffffff"
    )
    root3.attributes("-alpha", 0.8)
    root3.attributes("-topmost", True)
    root3.geometry("1920x1080+0+0")

    root3.update_idletasks()

    # 마우스 클릭 통과 설정
    hwnd = ctypes.windll.user32.GetParent(
        root3.winfo_id()
    )

    if not hwnd:
        hwnd = root3.winfo_id()

    GWL_EXSTYLE = -20
    WS_EX_LAYERED = 0x00080000
    WS_EX_TRANSPARENT = 0x00000020

    styles = ctypes.windll.user32.GetWindowLongW(
        hwnd, GWL_EXSTYLE
    )

    ctypes.windll.user32.SetWindowLongW(
        hwnd,
        GWL_EXSTYLE,
        styles | WS_EX_LAYERED | WS_EX_TRANSPARENT
    )

    # 화면 캡처에서 오버레이 제외
    if not exclude_window_from_capture(root3):
        logging.error(
            "Overlay capture exclusion failed"
        )
        root3.destroy()
        messagebox.showerror(
            "Error",
            "Cannot exclude overlay from capture."
        )
        return

    # 실행 상태 활성화
    overlay_running = True

    logging.info("Overlay started")

    # 반복 실행 시작
    schedule_next_capture()


#init()
mainGUI()

#pyautogui.screenshot('foo.png',region=(0,0, 300, 400))

#print(translate.Trans('Hello World!'))