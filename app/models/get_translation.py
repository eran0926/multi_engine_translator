import requests
import uuid
from bs4 import BeautifulSoup
# from app.models.log import get_logger
# from log import get_logger
import configparser
from pathlib import Path

# read config
config = configparser.ConfigParser(interpolation=None)
# config.read(Path('config/config.ini'))
config.read(Path(__file__).parent.parent.joinpath('config', 'config.ini'))


def get_page(url, header=None, params=None):
    header = header or {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    headers = requests.utils.default_headers()
    headers.update(header)
    r = requests.get(url, headers=headers, params=params)
    return r


def get_cambridge_translate(text=""):
    '''
    get cambridge dictionary translate
    '''
    text = text.replace(' ', '-')
    print(text)
    url = config["cambridge"]["base_url"] + text
    r = get_page(url)
    print(r.status_code)
    print(r.url)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "html.parser")
        page_body = soup.find("div", class_="di-body")

        trans = []

        for i in range(len(page_body.find_all("div", class_="di-title"))):
            tran = {}
            tran['from'] = page_body.find_all(
                "div", class_="di-title")[i].get_text()
            try:
                tran['pos'] = page_body.find_all("span", class_="pos dpos")[
                    i].get_text()
            except:
                tran['pos'] = None
            # tran['to'] = page_body.find_all(
            # tran['to'] =
            # sense-body

            tran['to'] = []
            # def_bodys = page_body.find_all("div", class_="sense-body")[i].find_all("div", class_="def-body")
            def_bodys = page_body.find_all(
                "div", class_="pr entry-body__el")[i].find_all("div", class_="def-body")
            for def_body in def_bodys:
                tran['to'].append(def_body.find(
                    "span", class_="trans").get_text())
            # .find_all("span", class_="trans").get_text()
            # .append(t.find("span", class_="trans").get_text())
            print(tran, '<<tran')
            trans.append(tran)

        if trans == []:
            return None
        return trans
    else:
        return None


def get_azure_translate(text="", ori_lan=None, tar_lan="zh-Hant"):
    if tar_lan == "":
        tar_lan = "zh-Hant"

    key = config["azure"]["key"]
    endpoint = config["azure"]["endpoint"]
    location = config["azure"]["location"]

    path = '/translate'
    constructed_url = endpoint + path

    params = {
        'api-version': '3.0',
        'to': tar_lan
    }

    if ori_lan != None and ori_lan != "":
        params['from'] = ori_lan

    headers = {
        'Ocp-Apim-Subscription-Key': key,
        # location required if you're using a multi-service or regional (not global) resource.
        'Ocp-Apim-Subscription-Region': location,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    body = [{
        'text': text
    }]

    r = requests.post(constructed_url, params=params,
                      headers=headers, json=body)
    print(r.status_code)
    if r.status_code == 200:
        response = r.json()
        return response[0]["translations"][0]["text"]
    else:
        return None


def get_translation(text, ori_lan=None, tar_lan="zh-Hant", engines=[]):
    engine_list = ["cambridge", "azure"]
    response = {}
    for engine in engines:
        if engine == "cambridge":
            response[engine] = get_cambridge_translate(text)
        elif engine == "azure":
            response[engine] = get_azure_translate(text, ori_lan, tar_lan)
        else:
            response[engine] = None
    return response


def get_predict_data(text):
    url = "https://dictionary.cambridge.org/zht/autocomplete/amp?dataset=english-chinese-traditional"
    params = {'q': text}
    r = get_page(url, params=params)
    if r.status_code == 200:
        response = r.json()
        return response
    else:
        return None


if __name__ == "__main__":
    # main_logger = get_logger("main")
    t = get_cambridge_translate('respect')
    # t = get_azure_translate("he")
    # get_predict_data("ap")
    print("-----------------------")
    print(t)
    # main_logger.debug(t)
