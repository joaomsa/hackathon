from bs4 import BeautifulSoup
import requests
import json
#import psycopg2

def get_projects_from_url(id, url):
    r = requests.get(url)
    if(r.ok == False): return None
    data = r.text
    soup = BeautifulSoup(data)
    return soup.findAll("div", {"class": "bill"})

def process_project_to_get_votes(projects):
    up = 0
    down = 0
    count = 0
    for p in projects:
        up_text = p.select('div.engagement > div.votes > small > span.up')[0].text.split()[0]
        down_text = p.select('div.engagement > div.votes > small > span.down')[0].text.split()[0]
        up_text = up_text.replace(".", "")
        down_text = down_text.replace(".", "")
        up += int(up_text)
        down += int(down_text)
        count += 1
    return count, up, down

def get_project_list(projects):
    returned = []
    for p in projects:
        tag = p.select('div.brief > div.tags')[0].text.strip()
        text = p.select('h2.summary > a')[0].text
        #print tag, text
        returned.append((tag, text))
    return returned

def submit_project_data(id, url):
    projects = get_projects_from_url(id, url)
    if(projects == None):
        data = { 'error' : True }
    else:
        count, up, down = process_project_to_get_votes(projects)
        project_list = get_project_list(projects)
        data = { 'num_projects' : count, 'up' : up, 'down' : down, 'url' : url, 'projects' : project_list }
    j = json.dumps(data)
    print j

    # dumping it
#    cur = conn.cursor()
#    cur.execute('INSERT INTO vote_na_web VALUES(' + id + ',' + data + ")")
    


#conn = psycopg2.connect("dbname='transparencia' user='joaosa' host='ec2-54-191-195-234.us-west-2.compute.amazonaws.com ' password='123456'")


#### TODO fazer script que coleta a pagina do candidato pelo nome

# Dilma
submit_project_data(1511105,'http://www.votenaweb.com.br/politicos/dilma.rousseff')

# Aecio
submit_project_data(1511086, 'http://www.votenaweb.com.br/politicos/aecio.neves')

# Marina silva
submit_project_data(1511083, 'http://www.votenaweb.com.br/politicos/marina.silva')

# Luciana 
submit_project_data(1511080, 'http://www.votenaweb.com.br/politicos/luciana.genro')
