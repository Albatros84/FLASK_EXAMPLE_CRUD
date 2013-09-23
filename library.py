from werkzeug import url_decode
from flask import Flask, render_template, request, redirect, url_for, flash
from flask.ext.sqlalchemy import SQLAlchemy

class MethodRewriteMiddleware(object):


    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        if 'METHOD_OVERRIDE' in environ.get('QUERY_STRING', ''):
            args = url_decode(environ['QUERY_STRING'])
            method = args.get('__METHOD_OVERRIDE__')
            if method:
                method = method.encode('ascii', 'replace')
                environ['REQUEST_METHOD'] = method
        return self.app(environ, start_response)


app = Flask(__name__)

#****************************************DATABASE*********

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255), unique=True)

    def __init__(self, name=None, description=None):
        self.name = name
        self.description = description

    def __repr__(self):
        return '<Name %r>' % self.name

#**********************************************************

app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'secret'
app.wsgi_app = MethodRewriteMiddleware(app.wsgi_app)

@app.route('/tasks')
def list_tasks():
    """GET /tasks

    Lists all tasks"""
    tasks=Task.query.all()
    return render_template('list_tasks.html', tasks=tasks)

@app.route('/tasks/<id>')
def show_task(id):
    """GET /tasks/<id>

    Get a task by its id"""
    task = Task.query.filter_by(id=id).first()
    return render_template('show_task.html', task=task)

@app.route('/tasks/new')
def new_task():
    """GET /tasks/new

    The form for a new task"""
    return render_template('new_task.html')

@app.route('/tasks', methods=['POST', 'GET'])
def create_task():
    """POST /tasks

    Receives a task data and saves it"""
    name = request.form['name']
    desc = request.form['desc']
    task=Task(name=name, description=desc)
    db.session.add(task)
    db.session.commit()
    flash('Task %s sucessful saved!' % task.name)
    return redirect(url_for('show_task', id=task.id))

@app.route('/tasks/<id>/edit')
def edit_task(id):
    """GET /tasks/<id>/edit

    Form for editing a task"""
    task=Task.query.filter_by(id=id).first()
    return render_template('edit_task.html', task=task)

@app.route('/tasks/<id>', methods=['PUT'])
def update_task(id):
    """PUT /tasks/<id>

    Updates a task"""
    task=Task.query.filter_by(id=id).first()
    task.description=request.form['desc']
    task.name = request.form['name'] # Save 
    db.session.add(task)
    db.session.commit()
    flash('Task %s updated!' % task.name)
    return redirect(url_for('show_task', id=task.id))

@app.route('/tasks/<id>', methods=['DELETE'])
def delete_task(id):
    """DELETE /tasks/<id>

    Deletes a task"""
    task=Task.query.filter_by(id=id).first()
    db.session.delete(task)
    db.session.commit()
    flash('Task %s deleted!' % task.name)
    return redirect(url_for('list_tasks'))

if __name__ == '__main__':
    app.run()
