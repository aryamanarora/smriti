from flask import Flask, render_template, request, redirect, url_for
from markupsafe import escape
from datetime import datetime, timedelta
import json
import markdown2
import humanize

app = Flask(__name__)

def dateconverter(o):
    if isinstance(o, datetime):
        return o.__str__()

data = []
with open('memories.json', 'r') as fin:
    data = json.load(fin)
    for i in range(len(data)):
        data[i]['natural'] = humanize.naturaldate(datetime.strptime(data[i]['date'], '%Y-%m-%d')).capitalize()

@app.route('/')
def index():
    return render_template('index.html', memories=data, entries=len(data))

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'GET':
        return render_template('add.html', id=len(data), added=False, failed=False)
    else:
        try:
            resp = json.loads(request.form['jsonval'])
            data.append({
                'title': resp['title'],
                'text': markdown2.markdown(resp['text']),
                'creation_date': datetime.now(),
                'modification_date': datetime.now(),
                'date': resp['date'],
                'people': resp['people'],
                'places': resp['places'],
                'natural': humanize.naturaldate(datetime.strptime(resp['date'], '%Y-%m-%d')).capitalize()
            })
            with open('memories.json', 'w') as fout:
                fout.write(json.dumps(data, indent=4, default=dateconverter))
            return render_template('add.html', id=len(data), added=True, failed=False)
        except:
            return render_template('add.html', id=len(data), added=False, failed=True)