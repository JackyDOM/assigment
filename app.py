from flask import Flask
from flask_restx import Api, Resource, fields, reqparse
from config import Config
from models import db, Department, Employee

config = Config()
app = Flask(__name__)
app.config.from_object(config)

# Initialize the Flask app context and create table
with app.app_context():
    db.init_app(app)
    db.create_all()

api = Api(app, version='1.0', title='Employee Directory', description='API manages employees')
api_ns = api.namespace("Reference", path='/apiv1', description='Reference Data')

# Define a data model for output marshalling
department_fields = api.model('Department', {
    'department_id': fields.Integer(description='The Department ID.'),
    'department_name': fields.String(description='The department name.')
})

# Define a data model for output marshalling for Employee
employee_fields = api.model('Employee', {
    'employee_id': fields.Integer(description='The employee ID'),
    'employee_name': fields.String(description='The employee name'),
    'employee_role': fields.String(description='The employee role'),
    'employee_information': fields.String(description='Additional employee information'),
    'department_id': fields.Integer(description='The department ID'),
    'department_name': fields.String(description='The department name'),
})

# Define a data model for input
put_department_parser = reqparse.RequestParser()
put_department_parser.add_argument('department_id', type=int, required=True, help='Department ID is required.')
put_department_parser.add_argument('department_name', type=str, required=True, help='Department name is required.')

# Define a data model for input
put_employee_parser = reqparse.RequestParser()
put_department_parser.add_argument('employee_id', type=int, required=True, help='Employee ID is required.')
put_department_parser.add_argument('employee_name', type=str, required=True, help='Employee Name is required.')
put_department_parser.add_argument('employee_role', type=str, required=True, help='Employee Role is required.')
put_department_parser.add_argument('employee_information', type=str, required=True, help='Employee Information is required.')
put_department_parser.add_argument('department_id', type=int, required=True, help='Department ID required.')
put_department_parser.add_argument('department_name', type=str, required=True, help='Department Name is required.')

@api_ns.route('/departments')
class AllDepartmentsResource(Resource):
    @api.marshal_with(department_fields)
    def get(self):
        departments = Department.query.all()
        return [{'department_id': department.department_id, 'department_name': department.department_name} for department in departments]


# Endpoint for retrieving all employees
@api.route('/employees')
class AllEmployeesResource(Resource):
    @api.marshal_with(employee_fields)
    def get(self):
        employees = Employee.query.all()
        return [
            {
                'employee_id': employee.employee_id,
                'employee_name': employee.employee_name,
                'employee_role': employee.employee_role,
                'employee_information': employee.employee_information,
                'department_id': employee.department_id,
                'department_name': employee.department_name
            }
            for employee in employees
        ]
 
@api.route('/swagger')
class SwaggerResource(Resource):
    def get(self):
        return api.swagger_ui()

if __name__ == '__main__':
    app.run(debug=True)
