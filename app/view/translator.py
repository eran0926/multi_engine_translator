from flask import Blueprint, render_template, jsonify, request
from app.models.log import get_logger
from app.models.get_translation import get_translation, get_predict_data

translator = Blueprint('translator', __name__)

logger = get_logger("view.translator", level="INFO")

def log_server_msg(msg):
    logger.info( "client_ip:" + request.environ["REMOTE_ADDR"] + " " + msg)

@translator.route('/')
def index():
    return render_template("translator.html")


@translator.route('/translator', methods=['POST'])
def tran():
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
            log_server_msg("Missing translator arg")
            return 'Missing arg', 400

        translation = get_translation(text, ori_lan, tar_lan, engines)
        log_server_msg("Using:\n" + \
                        "\tori_lan: " + str(ori_lan) + ",\n"\
                        "\ttar_lan: " + str(tar_lan) + ",\n"\
                        "\ttext   : " + str(text)    + ",\n"\
                        "\tengines :" + str(engines) + ",\n"\
                        "\tget translation: " + str(translation))
        re["translations"] = translation
        response_data.append(re)
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
