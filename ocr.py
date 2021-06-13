import easyocr

def ImagetoTxt(td, path, langCode):
    list1 = list()
    list1.append(langCode)
    reader = easyocr.Reader(list1)
    text = "\n".join(reader.readtext(path, detail = 0, paragraph=True))

    return text