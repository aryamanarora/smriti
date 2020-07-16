from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, timedelta
import json
import markdown2
import arrow

app = Flask(__name__)

@app.template_filter('fulldate')
def fulldate(x):
    return arrow.get(x).date().strftime("%B %-d, %Y")
@app.template_filter('natural')
def natural(x):
    return arrow.get(x).humanize()

def dateconverter(o):
    if isinstance(o, datetime):
        return o.__str__()

data = []
try:
    with open('memories.json', 'r') as fin:
        data = json.load(fin)
except:
    pass

@app.route('/')
def index():
    return render_template('index.html', memories=sorted(data, key=lambda d: datetime.strptime(d['date'], '%Y-%m-%d'), reverse=True), entries=len(data))

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'GET':
        return render_template('add.html', id=len(data), added=False, failed=False, memory=False)
    else:
        try:
            resp = json.loads(request.form['jsonval'])
            data.append({
                'title': resp['title'],
                'raw': resp['text'],
                'creation_date': datetime.now(),
                'modification_date': datetime.now(),
                'date': resp['date'],
                'people': resp['people'],
                'places': resp['places'],
                'images': resp['images'],
                'id': len(data)
            })
            with open('memories.json', 'w') as fout:
                fout.write(json.dumps(data, indent=4, default=dateconverter))
            return render_template('add.html', id=len(data), added=True, failed=False, memory=False)
        except:
            return render_template('add.html', id=len(data), added=False, failed=True, memory=False)

@app.route('/add/<code>', methods=['GET', 'POST'])
def edit(code):
    code = int(code)
    if request.method == 'GET':
        return render_template('add.html', id=len(data), added=False, failed=False, memory=data[code])
    else:
        try:
            resp = json.loads(request.form['jsonval'])
            data[code] = ({
                'title': resp['title'],
                'raw': resp['text'],
                'creation_date': data[code]['creation_date'],
                'modification_date': datetime.now(),
                'date': resp['date'],
                'people': resp['people'],
                'places': resp['places'],
                'images': resp['images'],
                'id': code
            })
            with open('memories.json', 'w') as fout:
                fout.write(json.dumps(data, indent=4, default=dateconverter))
            return render_template('add.html', id=code, added=True, failed=False, memory=data[code])
        except:
            return render_template('add.html', id=code, added=False, failed=True, memory=data[code])

@app.route('/memories/<code>')
def memory(code):
    code = int(code)
    text = markdown2.markdown(data[code]['raw'], extras=['smarty-pants', 'footnotes', 'toc', 'tables', 'fenced-code-blocks', 'break-on-newline'])
    if text == "<p></p>\n":
        text = None
    return render_template('memory.html', memory=data[code], text=text)

@app.route('/preview', methods=['POST'])
def preview():
    data = request.form['text']
    print(data)
    text = markdown2.markdown(str(data), extras=['smarty-pants', 'footnotes', 'toc', 'tables', 'fenced-code-blocks', 'break-on-newline'])
    return text