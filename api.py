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
    
    
user_agent = "topstukken-api/0.0.0"
base_url = "https://topstukken.naturalis.nl"
nba_url = "http://api.biodiversitydata.nl/v2"

@app.route('/getObject/<name>')
def get_object(name):
    enrich_nba = False
    if (request.args.get('nba')):
        if (request.args.get('nba').lower() == 'true'):
            enrich_nba=True
    return jsonify(get_specimen(name, enrich_nba=enrich_nba))
    
@app.route('/names')
def names():
    topstukken = get_topstukken(enrich=False)
    l = list(t['slug'] for t in topstukken)
    return jsonify(l)

@app.route('/objects')
def objects():
    enrich_nba = False
    if (request.args.get('nba')):
        if (request.args.get('nba').lower() == 'true'):
            enrich_nba=True
    topstukken = get_topstukken(enrich_nba=True)
    return jsonify(topstukken)

def get_specimen(name, enrich_nba=False):
    t_url = base_url + "/object/" + name
    t_json = parse_json_from_html(t_url)
    specimen = t_json['specimen']
    ## we don't want the related objects
    specimen.pop('related')
    if (enrich_nba):
        specimen['nba_specimen'] = get_nba_specimen(specimen['registrationNumber'])

    return specimen
    
def get_topstukken(enrich=True, enrich_nba=False):
    json_data = parse_json_from_html(base_url)
    topstukken = json_data['grid']['items']
    if (enrich):
        names = list(t['slug'] for t in topstukken)
        topstukken = list(map(lambda x: get_specimen(x, enrich_nba=enrich_nba), names))
    
    return topstukken

def get_nba_specimen(unitID):
    result = []
    url = nba_url + "/specimen/findByUnitID/" + unitID
    resp = requests.get(url, headers={'User-Agent': user_agent})
    if (resp.status_code >199 and resp.status_code <= 299):        
        result = json.loads(resp.content.decode())
    return result

def parse_json_from_html(url):
    resp = requests.get(url,headers={'User-Agent': user_agent})
    script_text = re.findall('(?si)<script type="text/javascript">(.*?)</script>', resp.content.decode())
    ## have to parse everything from var INITIAL_DATA
    initial_data = re.findall('.*INITIAL_DATA = (.*);', script_text[0])[0]
    json_data = json.loads(initial_data)
    return json_data

if __name__ == "__main__":
    app.run(host=ip, port=port)
