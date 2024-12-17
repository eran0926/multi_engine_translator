import configparser
from os import getenv
from pathlib import Path
import time
import uuid

import aiohttp
import asyncio
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from google.cloud import translate_v2 as translate
import requests

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


async def get_text_async(url, header=None, params=None):
    header = header or {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    headers = requests.utils.default_headers()
    headers.update(header)
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            return await response.text(), response.status, response.url


async def get_json_async(url, header=None, params=None):
    header = header or {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    headers = requests.utils.default_headers()
    headers.update(header)
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            return await response.json(), response.status, response.url


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

            if page_body.find_all("div", class_="pr entry-body__el"):
                def_bodys = page_body.find_all("div", class_="pr entry-body__el")[i].find_all(
                    "div", class_="dsense")  # 'pos-body'='pr entry-body__el'?
            else:
                def_bodys = page_body.find_all(
                    "span", class_="phrase-di-body dphrase-di-body")

            for def_body in def_bodys:
                tran['to'].append(def_body.find("div", "def-block ddef_block").find(
                    "span", class_="trans").get_text())
            trans.append(tran)

        if trans == []:
            return None
        return trans
    else:
        return None


async def get_cambridge_translate_async(row_text=""):
    '''
    get cambridge dictionary translate
    '''

    text = row_text.strip().replace(' ', '-').replace('/', '-')
    base_url = config["cambridge"]["base_url"]
    query_url = base_url + text
    page, status, url = await get_text_async(query_url)
    result = {
        "engine": "cambridge",
        "code": status,
        "ori": row_text,
        "translations": []
    }

    if status != 200:
        result["code"] = 600
        return result

    if str(url) != query_url:
        result["code"] = 404
        return result

    # TODO: parse html
    soup = BeautifulSoup(page, "html.parser")
    page_body = soup.find("div", class_="di-body")

    # def_bodys = page_body.find_all("div", class_="pr entry-body__el")
    # if not def_bodys:
    #     def_bodys = [page_body]
    def_bodys = page_body.find_all(
        "div", class_="pr entry-body__el") or [page_body]

    for i, def_body in enumerate(def_bodys):
        tran = {
            "ori": def_body.find("div", class_="di-title").get_text(),
            "pos": "",
            "trans": []
        }
        tran['ori'] = def_body.find("div", class_="di-title").get_text()
        try:
            tran['pos'] = page_body.find_all("span", class_="pos dpos")[
                i].get_text()
        except IndexError:
            pass

        sense_bodys = def_body.find_all("div", class_="sense-body dsense_b")
        if not sense_bodys:
            sense_bodys = def_body.find_all(
                "span", class_="phrase-di-body dphrase-di-body")

        for sense_body in sense_bodys:
            for def_block in sense_body.find_all("div", class_="def-block ddef_block", recursive=False):
                tran['trans'].append(def_block.find(
                    "span", class_="trans").get_text())
            # tran['tran'].append(de.find(
            #     "div", "def-block ddef_block").find("span", class_="trans").get_text())

        result["translations"].append(tran)
    return result


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
    # print(r.json())
    if r.status_code == 200:
        response = r.json()
        return response["data"]["translations"][0]["translatedText"]
    else:
        return None


async def get_google_translate_async(text="", ori_lan=None, tar_lan="zh-Hant"):
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

    res = {
        "engine": "google",
        "code": 200,
        "tran": ""
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(endpoint, params=params, headers=headers, json=body) as response:
            if response.status == 200:
                r = await response.json()
                res["tran"] = r["data"]["translations"][0]["translatedText"]
                return res
            else:
                res["code"] = 600
                return res


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


async def get_azure_translate_async(text="", ori_lan=None, tar_lan="zh-Hant"):
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

    res = {
        "engine": "azure",
        "code": 200,
        "tran": ""
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(constructed_url, params=params, headers=headers, json=body) as response:
            if response.status == 200:
                r = await response.json()
                res["tran"] = r[0]["translations"][0]["text"]
                return res
            else:
                res["code"] = 600
                return res


def get_translation(text, ori_lan=None, tar_lan="zh-Hant", engines=[]):
    # logger.debug(engines)
    response = {}
    for engine in engines:
        if engine == "cambridge" and ori_lan == "en":
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


async def get_translation_async(text, ori_lan=None, tar_lan="zh-Hant", engines=[]):
    # logger.debug(engines)
    response = {}
    tasks = []
    for engine in engines:
        if engine == "cambridge" and ori_lan == "en":
            tasks.append(get_cambridge_translate_async(text))
        elif engine == "azure":
            tasks.append(get_azure_translate_async(text, ori_lan, tar_lan))
        elif engine == "google":
            tasks.append(get_google_translate_async(text, ori_lan, tar_lan))
    # logger.info(response)
    results = await asyncio.gather(*tasks)

    return results

if __name__ == "__main__":
    # main_logger = get_logger("main")
    # t = get_cambridge_translate('how are you?')
    # t = get_cambridge_translate('hi')
    # t = get_cambridge_translate('honour')
    # t = get_cambridge_translate('read')
    # t = get_cambridge_translate('how-about')
    # t = get_azure_translate("he")
    # get_predict_data("ap")
    # t = get_translation("How are you?", engines=["google", "azure", "cambridge"], ori_lan="en")
    # t = get_translation("Hoefefefefefefefefe?as", engines=[ "cambridge"])
    # print("-----------------------")
    # print(t)
    # main_logger.debug(t)
    w = ['how are you?', 'hi', 'honour', 'read', 'how-about',
         'explain something away', 'explanatory variable']

    # for i in w:
    #     print(i)
    #     print(get_cambridge_translate(i))
    #     print('-'*50)
    #     print(asyncio.run(get_cambridge_translate_async(i)))
    #     # print("====================================")
    #     print("====================================")

    # start_time = time.time()
    # for i in w:
    #     get_cambridge_translate(i)
    # print("Time used: ", time.time()-start_time)

    # async def main():
    #     start_time = time.time()
    #     tasks = [get_cambridge_translate_async(i) for i in w]
    #     results = await asyncio.gather(*tasks)
    #     for r in results:
    #         print(r)
    #         print("====================================")
    #     print("Time used: ", time.time()-start_time)
    # asyncio.run(main())

    # start_time = time.time()
    # print(get_azure_translate("he"))
    # print(get_azure_translate("he"))
    # print("Azure sync used: ", time.time()-start_time)

    # async def azure_async_test():
    #     start_time = time.time()
    #     tasks = [get_azure_translate_async("he") for i in range(2)]
    #     results = await asyncio.gather(*tasks)
    #     for r in results:
    #         print(r)
    #         # print("====================================")
    #     print("Azure async used: ", time.time()-start_time)
    # asyncio.run(azure_async_test())

    # start_time = time.time()
    # print(get_google_translate("how are you"))
    # print(get_google_translate("he"))
    # print("Google sync used: ", time.time()-start_time)

    # async def google_async_test():
    #     start_time = time.time()
    #     tasks = [get_google_translate_async("how about") for i in range(1)]
    #     results = await asyncio.gather(*tasks)
    #     for r in results:
    #         print(r)
    #         # print("====================================")
    #     print("Google async used: ", time.time()-start_time)
    # asyncio.run(google_async_test())

    start_time = time.time()
    print(get_translation("how are you", engines=[
          "google", "azure", "cambridge"], ori_lan="en"))
    print("All sync used: ", time.time()-start_time)

    async def all_async_test():
        start_time = time.time()
        tasks = [get_translation_async("how are you", engines=[
                                       "google", "azure", "cambridge"], ori_lan="en") for i in range(1)]
        results = await asyncio.gather(*tasks)
        for r in results:
            print(r)
            # print("====================================")
        print("All async used: ", time.time()-start_time)
    asyncio.run(all_async_test())
