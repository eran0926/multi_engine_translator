from flask import Blueprint, render_template, jsonify, request
from app.models.log import get_logger
from app.models.get_translation import get_translation, get_predict_data

translator = Blueprint('translator', __name__)


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
            return 'Missing arg', 400

        re["translations"] = get_translation(text, ori_lan, tar_lan, engines)
        response_data.append(re)
    return jsonify(response_data)


@translator.route('/get_predicts')
def get_predicts():
    response = get_predict_data(request.args['q'])
    # print(response)
    return jsonify(response)


@translator.route('/get_history')
def get_history():
    return jsonify()


@translator.route('/test')
def test():
    return jsonify(["a", "b"])
