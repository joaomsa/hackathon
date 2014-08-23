from bs4 import BeautifulSoup
import requests
import json

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

def process_text(text):
    tokens = text.split(',')
    if len(tokens) < 2: return text

    c = 0
    returned = tokens[0]

    while len(returned) < 75:
        if len(tokens) == c: return text

        c += 1
        returned += "," + tokens[c]

    return returned + "."


def get_project_list(projects):
    returned = []
    for p in projects:
        tag = p.select('div.brief > div.tags')[0].text.strip()
        text = p.select('h2.summary > a')[0].text

        text = process_text(text)
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
    return data

def get_project_data(id):
    dic = {
        "1511105" : 'http://www.votenaweb.com.br/politicos/dilma.rousseff',
        "1511086" : 'http://www.votenaweb.com.br/politicos/aecio.neves',
        "1511083" : 'http://www.votenaweb.com.br/politicos/marina.silva',
        "1511080" : 'http://www.votenaweb.com.br/politicos/luciana.genro'
        }
    try:
        return submit_project_data(id, dic[id])
    except KeyError:
        return None

if __name__ == "__main__":
    from pprint import pprint
    pprint(get_project_data("1511105"))
    print 10 * "#"
    pprint(get_project_data("1511086"))
