from waitress import serve
from app import create_app

app = create_app('testing')


# @app.route('/')
# def hello_world():
#     return 'Hello World!'


if __name__ == '__main__':
    # app.run("0.0.0.0", 80)
    serve(app, host='0.0.0.0', port=8080)
