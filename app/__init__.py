import os
import multiprocessing

from flask import Flask, Blueprint, jsonify, render_template, request
from flask_api import status

from app.riot import Riot


def create_app(*args):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = "App_secret_key!"
    # ensure the instance folder exists
    try:
        if not os.path.exists(app.instance_path):
            os.makedirs(app.instance_path)
    except OSError as _:
        print(str(_))

    index = Blueprint('lookup', __name__, url_prefix='/lookup')

    @index.route('/', methods=['GET', 'POST'])
    def riot():
        valid_servers = ['euw1', 'na1', 'eun1', 'br1', 'la1', 'la2', 'tr1', 'jp1', 'kr', 'ru', 'oc1']
        semaphore = multiprocessing.Semaphore(10)
        
        if request.method == 'GET':
            return render_template("app/root.html", server=valid_servers)
        elif request.method == "POST":
            info = request.form
            semaphore.acquire()
            result = multiprocessing.Manager().dict()
            background_job = multiprocessing.Process(target=form_data_manipulation,
                                                    args=(info, semaphore, result))                                                                                                                                                            
            background_job.start()
            background_job.join()
            print(dict(result))
            print("LEL")
            return render_template("app/root.html", result=dict(result), server=valid_servers)

    
    def form_data_manipulation(info, semaphore, result):
        """
        manipulates the form data here.
        """
        riot_api = info['riot_api'] if 'riot_api' in info else None
        account_name = info['account_name'] if 'account_name' in info else None
        server = info['servers'] if 'servers' in info else None

        riot = Riot(account_name, server, riot_api)
        result = riot.master_controller()
        print(dict(result))
        print("L00000L")
        semaphore.release()

    @app.route("/")
    def root():
        return "Homie! You are in the 'riot' place, but at the wrong time!"

    app.register_blueprint(index)
    return app


if __name__ == "__main__":
    app = create_app()
    app.run()
