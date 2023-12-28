#modificado caho .02/05/2023
import flask
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from funciones import mainRutas
import json



def jsonp(func):
    def decorated_function(*args, **kwargs):
        return flask.jsonify(func(*args, **kwargs))

    return decorated_function


app = Flask(__name__)


@app.route('/hola')
def hello_world():  # put application's code here
    return 'Nada que ver acá, circule!'


@app.route('/', methods=['POST'])
@cross_origin(allow_headers=['Content-Type'])
def getDataSources():  # put application's code here

    if request.is_json:
        json_data = request.get_json()       
        rutas = mainRutas(json_data);
        #rutas = mainRutas();
        return jsonify(rutas)
    else:
        return 'No se recibió un JSON'
    
    data = request.args.get("data")
    
   



@app.route('/opperouter', methods=['POST'])
@cross_origin(allow_headers=['Content-Type'])
def getDataSourcesr():  # put application's code here

    if request.is_json:
        json_data = request.get_json()
        rutas = mainRutas(json_data);
        #rutas = mainRutas();
        return jsonify(rutas)
    else:
        return 'No se recibió un JSON'

    data = request.args.get("data")

    

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=9956)
