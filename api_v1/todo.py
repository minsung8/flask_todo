from flask import jsonify
from flask import request, session
from flask import Blueprint
from models import Todo, db, Fcuser
import datetime
import requests
from . import api

def send_slack(msg):
    res = requests.post('https://hooks.slack.com/services/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', json={
        'text': msg
    }, headers={'Content-Type': 'application/json'})

@api.route('/todos/done', methods=['PUT'])
def todos_done():
    userid = session.get('userid', 1)
    if not userid:
        return jsonify(), 401

    data = request.get_json()
    todo_id = data.get('todo_id')

    todo = Todo.query.filter_by(id=todo_id).first()
    fcuser = Fcuser.query.filter_by(userid=userid).first()

    if todo.fcuser_id != fcuser.id:
        return jsonify(), 400

    todo.status = 1
    
    db.session.commit()

    return jsonify()

@api.route('/todos', methods=['POST', 'GET', 'DELETE'])
def todos():
    userid = session.get('userid', 1)
    if not userid:
        return jsonify(), 401

    if request.method == 'POST':
        data = request.get_json()
        todo = Todo()
        todo.title = data.get('title')

        fcuser = Fcuser.query.filter_by(userid=userid).first()
        todo.fcuser_id = fcuser.id

        todo.due = data.get('due')
        todo.status = 0

        db.session.add(todo)
        db.session.commit()

        send_slack('Todo가 생성되었습니다.')

    elif request.method == 'GET':
        todos = Todo.query.filter_by(fcuser_id=userid)
        return jsonify([i.serialize for i in todos])

    elif request.method == 'DELETE':
        data = request.get_json()
        todo_id = data.get('todo_id')

        todo = Todo.query.filter_by(id=todo_id).first()

        db.session.delete(todo)
        db.session.commit()

        return jsonify(), 203

    return jsonify(data)

@api.route('/slack/todos', methods=['POST'])
def slack_todo():
    res = request.form['text'].split(' ')
    cmd, *args = res

    ret_msg = ''
    if cmd == 'create':
        todo_name = args[0]

        todo = Todo()
        todo.title = todo_name

        db.session.add(todo)
        db.session.commit()
        ret_msg = 'Todo가 생성되었습니다'
        send_slack('[%s] "%s"할 일을 만들었습니다 '% (str(datetime.datetime.now()), todo_name))

    elif cmd == 'list':
        todos = Todo.query.all()
        for i, todo in enumerate(todos):
            ret_msg += '%d. %s (~ %s)\n' % (i + 1, todo.title, str(todo.tstamp))
    
    return ret_msg