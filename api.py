import requests
import re
import json
from flask import Flask
from flask import request, make_response, render_template, jsonify
from os import environ

app = Flask(__name__)

try:
    ip = environ['TOP_API_IP']
    port = environ['TOP_API_PORT']
except Exception as e:
    ip = '0.0.0.0'
    port = '5000'
    print('TOP_API_IP and TOP_API_PORT not set')
    print('Defaulting to ' + ip + ':' + port)
    print(e)
    

base_url = "https://topstukken.naturalis.nl"

@app.route('/getObject/<name>')
def get_object(name):
    return jsonify(get_specimen(name))
    
@app.route('/names')
def names():
    topstukken = get_topstukken(enrich=False)
    l = list(t['slug'] for t in topstukken)
    return jsonify(l)

@app.route('/objects')
def objects():
    topstukken = get_topstukken()
    return jsonify(topstukken)

def get_specimen(name):
    t_url = base_url + "/object/" + name
    t_json = parse_json_from_html(t_url)
    specimen = t_json['specimen']
    ## we don't want the related objects
    specimen.pop('related')
    return specimen
    
def get_topstukken(enrich=True):
    json_data = parse_json_from_html(base_url)
    topstukken = json_data['grid']['items']
    if (enrich):
        names = list(t['slug'] for t in topstukken)
        topstukken = list(map(lambda x: get_specimen(x), names))
    return topstukken
    
def parse_json_from_html(url):
    resp = requests.get(url,headers={'User-Agent':'Mozilla/5.0'})
    script_text = re.findall('(?si)<script type="text/javascript">(.*?)</script>', resp.content.decode())    
    ## have to parse everything from var INITIAL_DATA
    initial_data = re.findall('.*INITIAL_DATA = (.*);', script_text[0])[0]
    json_data = json.loads(initial_data)
    return json_data

if __name__ == "__main__":
    app.run(host=ip, port=port)




