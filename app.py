import psycopg2
import json
import requests
import vote_na_web
from flask import Flask, send_from_directory, request, Response

APP_TOKEN = "vQtVQakNXGqZ"
APP_SECRET = "ArbNezEPBRPF"

app = Flask(__name__)
app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["pg_dsn"] = "dbname='transparencia' user='joaosa' host='ec2-54-191-195-234.us-west-2.compute.amazonaws.com' password='123456' port=19000"

@app.route("/search")
def search_name():
    name = request.args.get('nome')
    with psycopg2.connect(app.config['pg_dsn']) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                    select
                        similarity(%s, data->>'nome') as sim ,
                        data->>'nome' as nome , data->>'id' as id,
                        data->>'foto' as foto,
                        cast(data->>'previsao' as float) as prev
                    from candidatos_json
                    where data->>'cargo' = 'Presidente'
                    order by sim desc, prev desc
                    limit 10""", [name])
            rows = cur.fetchall()
            results = [{'id': row[2], 'nome': row[1], 'foto': row[3]} for row in rows]
            return json.dumps(results)

@app.route("/candidatura")
def canditadura():
    cid = request.args.get('id')
    data = { "projeto": projeto(cid),
            "bio": bio(cid),
            "historico": historico(cid)
    }
    return Response(json.dumps(data), mimetype='application/json')

def projeto(id):
    return vote_na_web.get_project_data(id)

def bio(id):
    id = request.args.get('id')
    api_url = "http://api.transparencia.org.br/api/v1/candidatos"
    parameters = {}
    header = {"APP-token": APP_TOKEN}
    r = requests.get(
        "/".join([api_url,id]),
        params=parameters,
        headers=header
    )
    response = json.loads(r.text)
    result = {}
    for key in response:
        if key in ['apelido','nome','miniBio','partido','cargo','reeleicao','bancadas','cargos', 'id', 'foto','estado']:
            result[key] = response[key]
    return result

def historico(id):
    api_url = "http://api.transparencia.org.br/api/v1/candidatos"
    parameters = {}
    header = {"APP-token": APP_TOKEN}
    r = requests.get(
        "/".join([api_url,id,"candidaturas"]),
        params=parameters,
        headers=header
    )
    response = json.loads(r.text)
    candidaturas = []
    for candidatura in response:
        candidaturas.append([candidatura['anoEleitoral'],candidatura['cargo'], candidatura['resultado']])

    r = requests.get(
        "/".join([api_url,id]),
        params=parameters,
        headers=header
    )
    response = json.loads(r.text)
    if response.has_key('processos'):
        processos = response['processos']
    else:
        processos = None

    r = requests.get(
        "/".join([api_url,id,'estatisticas']),
        params=parameters,
        headers=header
    )
    response = json.loads(r.text)
    if response:
        faltas_com = response['faltas_com']
        faltas_plen = response['faltas_plen']
    else:
        faltas_com = None
        faltas_plen = None
    return { 'candidaturas': candidaturas, 'processos': processos,
            'faltas_plen': faltas_plen, 'faltas_com': faltas_com }


@app.route("/", defaults={"path": "index.html"})
@app.route("/<path:path>")
def assets(path):
    return send_from_directory("static", path)


if __name__ == "__main__":
    app.run()
