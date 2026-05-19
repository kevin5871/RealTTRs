import easyocr

def ImagetoTxt(td, path, langCode):
    list1 = list()
    list1.append(langCode)
    reader = easyocr.Reader(list1)
    text = reader.readtext(path)
    text_detail = reader.readtext(path, detail=0)
    return text, text_detail