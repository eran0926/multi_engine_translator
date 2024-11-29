import requests
import aiohttp
import asyncio
import uuid
from bs4 import BeautifulSoup
import configparser
from pathlib import Path
from google.cloud import translate_v2 as translate
from os import getenv
from dotenv import load_dotenv

load_dotenv()

try:
    from .log import get_logger
except ImportError:
    from log import get_logger
    print("Using absoloute import")

# read config
config = configparser.ConfigParser(interpolation=None)
config.read(Path(__file__).parent.parent.joinpath('config', 'config.ini'))

logger = get_logger("get_translation")

def get_page(url, header=None, params=None):
    header = header or {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    headers = requests.utils.default_headers()
    headers.update(header)
    r = requests.get(url, headers=headers, params=params)
    return r


async def get_page_async(url, header=None, params=None):
    header = header or {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    headers = requests.utils.default_headers()
    headers.update(header)
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            return await response

def get_predict_data(text):
    url = "https://dictionary.cambridge.org/zht/autocomplete/amp?dataset=english-chinese-traditional"
    params = {'q': text}
    r = get_page(url, params=params)
    if r.status_code == 200:
        response = r.json()
        return response
    else:
        return None

def get_cambridge_translate(text=""):
    '''
    get cambridge dictionary translate
    '''
    text = text.replace(' ', '-')
    base_url = config["cambridge"]["base_url"]
    url = base_url + text
    r = get_page(url)

    if r.status_code == 200 and r.url != base_url:
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

            tran['to'] = []
            
            if page_body.find_all("div", class_="pr entry-body__el") :
                def_bodys = page_body.find_all("div", class_="pr entry-body__el")[i].find_all("div", class_="dsense")  # 'pos-body'='pr entry-body__el'?
            else:
                def_bodys = page_body.find_all("span", class_="phrase-di-body dphrase-di-body")

            for def_body in def_bodys:
                tran['to'].append(def_body.find("div", "def-block ddef_block").find(
                    "span", class_="trans").get_text())
            trans.append(tran)

        if trans == []:
            return None
        return trans
    else:
        return None
    
async def get_cambridge_translate_async(text=""):
    '''
    get cambridge dictionary translate
    '''
    text = text.replace(' ', '-')
    base_url = config["cambridge"]["base_url"]
    url = base_url + text
    r = await get_page_async(url)

    result = {
        "engine": "cambridge",
        "statua_code": r.status,
        "ori": text,
        "translations": []
    }

    if r.status != 200 or r.url == base_url:
        return result
    
    # TODO: parse html


def get_google_translate(text="", ori_lan=None, tar_lan="zh-Hant"):
    if tar_lan == "":
        tar_lan = "zh-Hant"

    api_key = getenv("GOOGLE_TRANSLATION_API_KEY")
    endpoint = config["google"]["endpoint"]


    headers = {
        'Content-type': 'application/json; charset=utf-8'
    }

    params = {
        'key': api_key
    }

    body = {
        "q": text,
        "target": tar_lan
    }

    r = requests.post(endpoint, params=params, headers=headers, json=body)
    print(r.json())
    if r.status_code == 200:
        response = r.json()
        return response["data"]["translations"][0]["translatedText"]
    else:
        return None

def get_azure_translate(text="", ori_lan=None, tar_lan="zh-Hant"):
    if tar_lan == "":
        tar_lan = "zh-Hant"

    api_key = getenv("AZURE_TRANSLATION_API_KEY")
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
        'Ocp-Apim-Subscription-Key': api_key,
        'Ocp-Apim-Subscription-Region': location,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    body = [{
        'text': text
    }]

    r = requests.post(constructed_url, params=params,
                      headers=headers, json=body)
    if r.status_code == 200:
        response = r.json()
        return response[0]["translations"][0]["text"]
    else:
        return None


def get_translation(text, ori_lan=None, tar_lan="zh-Hant", engines=[]):
    # logger.debug(engines)
    response = {}
    for engine in engines:
        if engine == "cambridge" and ori_lan =="en":
            r = get_cambridge_translate(text)
            if r:
                response[engine] = r
        elif engine == "azure":
            r = get_azure_translate(text, ori_lan, tar_lan)
            if r:
                response[engine] = r
        elif engine == "google":
            r = get_google_translate(text, ori_lan, tar_lan)
            if r:
                response[engine] = r
    # logger.info(response)
    return response




if __name__ == "__main__":
    # main_logger = get_logger("main")
    # t = get_cambridge_translate('how are you?')
    # t = get_cambridge_translate('hi')
    t = get_cambridge_translate('honour')
    # t = get_azure_translate("he")
    # get_predict_data("ap")
    # t = get_translation("How are you?", engines=["google", "azure", "cambridge"], ori_lan="en")
    # t = get_translation("Hoefefefefefefefefe?as", engines=[ "cambridge"])
    print("-----------------------")
    print(t)
    # main_logger.debug(t)
