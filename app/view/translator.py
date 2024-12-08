import asyncio

from flask import Blueprint, render_template, jsonify, request

from app.models.log import get_logger
from app.models.get_translation import get_translation, get_translation_async, get_predict_data

translator = Blueprint('translator', __name__)

logger = get_logger("view.translator", level="INFO", queue_handler=True)


def log_server_msg(msg):
    logger.info("client_ip:" + request.environ["REMOTE_ADDR"] + " " + msg)


@translator.route('/')
def index():
    return render_template("translator.html")


@translator.route('/get_translation', methods=['POST'])
def get_tran():
    request_data = request.get_json()
    response_data = list()
    for data in request_data:
        re = dict()
        try:
            ori_lan = data["from"]
            tar_lan = data["to"]
            text = data["text"]
            engines = data["engines"]
        except:
            # log_server_msg("Missing translator arg")
            return jsonify({"error": {"code": 400, "message": "Missing arg"}}), 400

        translation = get_translation(text, ori_lan, tar_lan, engines)
        log_server_msg("Using:\n" +
                       "\tori_lan: " + str(ori_lan) + ",\n"
                       "\ttar_lan: " + str(tar_lan) + ",\n"
                       "\ttext   : " + str(text) + ",\n"
                       "\tengines :" + str(engines) + ",\n"
                       "\tget translation: " + str(translation))
        re["translations"] = translation
        response_data.append(re)
    return jsonify(response_data)


@translator.route('/get_translation_async', methods=['POST'])
async def get_tran_async():
    request_data = request.get_json()
    response_data = {"data": {"translations": []}}
    tasks = []
    for i, data in enumerate(request_data):
        try:
            ori_lan = data["from"]
            tar_lan = data["to"]
            text = data["text"]
            engines = data["engines"]
        except:
            # log_server_msg("Missing translator arg")
            return jsonify({"error": {"code": 400, "message": f"Missing arg at data {i}"}}), 400
        tasks.append(get_translation_async(text, ori_lan, tar_lan, engines))

    r = await asyncio.gather(*tasks)

    for translation in r:
        log_server_msg("Using:\n" +
                       "\tori_lan: " + str(ori_lan) + ",\n"
                       "\ttar_lan: " + str(tar_lan) + ",\n"
                       "\ttext   : " + str(text) + ",\n"
                       "\tengines :" + str(engines) + ",\n"
                       "\tget translation: " + str(translation))
        response_data["data"]["translations"].append(translation)

    return jsonify(response_data)


@translator.route('/get_predicts')
def get_predicts():
    query = request.args['q']
    log_server_msg("get_predicts with query:" + query)
    response = get_predict_data(query)
    # print(response)
    return jsonify(response)


@translator.route('/get_history')
def get_history():
    return jsonify()


@translator.route('/test')
def test():
    return jsonify(["a", "b"])
