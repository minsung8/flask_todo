from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Todo(db.Model):
    __tablename__ = 'todo'

    id = db.Column(db.Integer, primary_key=True)
    fcuser_id = db.Column(db.Integer, db.ForeignKey('fcuser.id'), nullable=False)
    title = db.Column(db.String(256))
    status = db.Column(db.Integer)
    due = db.Column(db.String(64))
    tstamp = db.Column(db.DateTime, server_default=db.func.now())

    @property
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'fcuser': self.fcuser.userid,
            'tstamp': self.tstamp
        }

class Fcuser(db.Model):
    __tablename__ = 'fcuser'
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String(32))
    password = db.Column(db.String(128))
    todos = db.relationship('Todo', backref='fcuser', lazy=True)