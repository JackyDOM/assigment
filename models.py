from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# create 2 tables
class Department(db.Model):
  __tablename__ = "department"
  department_id = db.Column(db.Integer, primary_key = True)
  department_name = db.Column(db.String(50), nullable=False)
  
class Employee(db.Model):
  __tablename__ = "employee"
  employee_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  employee_name = db.Column(db.String(45), nullable=False)
  employee_role = db.Column(db.String(45), nullable=False)
  employee_information = db.Column(db.String(200), nullable=True)
  department_id = db.Column(db.Integer, db.ForeignKey('department.department_id'), nullable=False)
  
  department = db.relationship('Department', backref=db.backref('employees', lazy=True))