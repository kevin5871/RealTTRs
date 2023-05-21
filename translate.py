import requests
import base64
import hashlib
import hmac
import time
import uuid
import json
import logging
import requests

def Trans(text, start, target, key1) :
    try :
        s = requests.Session()

        timestamp = int(time.time() * 1000)
        deviceId = str(uuid.uuid4())

        key = key1
        msg1 = bytes(deviceId, encoding='utf8') + b'\nhttps://papago.naver.com/apis/langs/dect\n' + bytes(str(timestamp), encoding='utf8')
        msg2 = bytes(deviceId, encoding='utf8') + b'\nhttps://papago.naver.com/apis/n2mt/translate\n' + bytes(str(timestamp), encoding='utf8')

        h1 = hmac.new(key, msg1, hashlib.md5)
        hd1 = base64.b64encode(h1.digest()).decode("UTF-8")

        h2 = hmac.new(key, msg2, hashlib.md5)
        hd2 = base64.b64encode(h2.digest()).decode("UTF-8")

        s.get('https://papago.naver.com/')

        headers={
        'Authorization': f'PPG {deviceId}:{hd1}',
        'Timestamp': str(timestamp),
        'device-type': 'pc'
        }
        lang = s.post('https://papago.naver.com/apis/langs/dect',{'query' : text} ,headers = headers)
        #print(json.loads(lang.text))
        langCode = json.loads(lang.text)['langCode']
        if langCode != start :
            logging.warning("Different Language Detected (Detected - %s | Actual - %s)"%(langCode, start))

        headers={
        'Authorization': f'PPG {deviceId}:{hd2}',
        'Timestamp': str(timestamp),
        'device-type': 'pc'
        }
        content = {
        'deviceId': deviceId,
        'locale': 'en-US',
        'dict': 'false',
        'dictDisplay': '0',
        'honorific': 'false',
        'instant': 'false',
        'paging': 'false',
        'source': langCode,
        'target': target,
        'text': text
        }

        res = s.post('https://papago.naver.com/apis/n2mt/translate', content, headers=headers)

        #print(json.loads(res.text)['translatedText'])
        return json.loads(res.text)['translatedText']
    except :
        try :
            return json.loads(lang.text)['code'] + '|' + json.loads(lang.text)['message'] + '|' +  json.loads(lang.text)['displayMessage']
        except :
            logging.error(json.dumps(lang.text))
            return json.dumps(lang.text)

def getKey() :
    URL = 'http://papago.naver.com'
    response = requests.get(URL)
    txt = response.text
    txt = txt.split("\n")
    links = list()
    #print(txt, len(txt))
    for i in range(0, len(txt)) :
        if "If you're" in txt[i] :
            txt = txt[i]

    txt = txt.split(" ")
    for i in range(0, len(txt)) :
        if 'main' in txt[i] and 'src' in txt[i] :
            links.append(txt[i])

    for i in range(0,len(links)) :
        links[i] = links[i].replace('src="', '')
        links[i] = links[i].replace('"','')

    for i in range(0, len(links)) :
        URL = 'http://papago.naver.com' + links[i]
        response = requests.get(URL)
        txt = response.text
        logging.info(URL)
        if 'AUTH_KEY' in str(txt) :
            txt = txt.split(',')
            for i in range(0, len(txt)) :
                    if 'AUTH_KEY' in str(txt[i]) :
                        #print(txt[i])
                        keyst = txt[i].split('"')
                        #print(keyst)
                        for j in range(0, len(keyst)) :
                            if 'v' in keyst[j] :
                                key = keyst[j]
                                break
                    else :
                        continue
        else :
            continue
    logging.info("KEY FIND : %s"% key)
    return key.encode('ascii')


if __name__ == "__main__" :
    string = str(input())
    print(Trans(string, "ko", "en", getKey()))