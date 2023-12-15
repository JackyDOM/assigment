from flask import Flask
# from flask_restx import Api, Resource, fields, reqparse
# from sqlalchemy import exc
# from config import Config
# from models import db, Department, Employee

# config = Config()
app = Flask(__name__)
# app.config.from_object(Config)

# #Initialize the flask app context and create tables
# with app.app_context():
#     db.init_app(app)
#     db.create_all()
    
# api = Api(app, version='1.0', title='Employee Directory API', description='')

@app.route('/')
def hello():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(debug=True)
