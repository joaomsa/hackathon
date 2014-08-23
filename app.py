import psycopg2
import json
from flask import Flask, send_from_directory, request

app = Flask(__name__)
app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["pg_dsn"] = "dbname='transparencia' user='joaosa' host='ec2-54-191-195-234.us-west-2.compute.amazonaws.com' password='123456' port=19000"


@app.route("/search")
def search_name():
    name = request.args.get('nome')
    with psycopg2.connect(app.config['pg_dsn']) as conn:
        with conn.cursor() as cur:
            cur.execute("select similarity(%s, data->>'nome') as sim , data->>'nome' as nome , data->>'id' as id, data->>'foto' as foto from candidatos_json order by sim desc limit 10", [name])
            rows = cur.fetchall()
            results = [{'id': row[2], 'nome': row[1], 'foto': row[3]} for row in rows]
            return json.dumps(results)

@app.route("/candidato/<string:id>")
def candidato(id):
    try:
	   conn = psycopg2.connect(app.config['pg_dsn'])
    except:
	   return

    cur = conn.cursor()
    cur.execute("""SELECT data->>'nome' from candidatos_json where data->>'nome' ilike '%dilma%';""")
    rows = cur.fetchall()
    return rows[0]

@app.route("/", defaults={"path": "index.html"})
@app.route("/<path:path>")
def assets(path):
    return send_from_directory("static", path)


if __name__ == "__main__":
    app.run()
