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
                        data->>'foto' as foto
                    from candidatos_json
                    where data->>'cargo' = 'Presidente'
                    order by sim desc limit 10""", [name])
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
    with psycopg2.connect(app.config['pg_dsn']) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT data->>'id', data->>'apelido', data->>'nome', data->>'miniBio', data->>'partido', \
                data->>'reeleicao', data->>'bancadas', data->>'cargos', data->>'foto', \
                data->>'estado' from candidatos_json where data->>'id' =%s;", [id])
            rows = cur.fetchall()
            row = rows[0]
            result = {'id': row[0], 'apelido': row[1], 'nome': row[3], 'miniBio': row[4], 'partido':row[5],
                    'reeleicao': row[6], 'bancadas':row[7], 'cargos': row[8], 'foto': row[9]}
    return result

def historico(id):

    with psycopg2.connect(app.config['pg_dsn']) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT data->>'anoEleitoral', data->>'cargo', data->>'resultado' from (select id, json_array_elements(data) as data from candidaturas_json) as subq where data->>'id' =%s;", [id])
            rows = cur.fetchall()
            candidaturas = []
            for candidatura in rows:
                candidaturas.append([candidatura[0],candidatura[1], candidatura[2]])
            cur.execute("SELECT data->>'anoEleitoral', data->>'cargo', data->>'resultado' from (select id, json_array_elements(data) as data from estatisticas_json) as subq where data->>'id' =%s;", [id])
            rows = cur.fetchall()
            if rows:
                faltas_com = rows['faltas_com']
                faltas_plen = rows['faltas_plen']
            else:
                faltas_com = None
                faltas_plen = None
            cur.execute("SELECT data->>'processos' from candidatos_json where data->>'id' =%s;", [id])
            rows = cur.fetchall()
            processos = [row[0] for row in rows]
    return { 'candidaturas': candidaturas, 'processos': processos,
            'faltas_plen': faltas_plen, 'faltas_com': faltas_com }


@app.route("/", defaults={"path": "index.html"})
@app.route("/<path:path>")
def assets(path):
    return send_from_directory("static", path)


if __name__ == "__main__":
    app.run()
