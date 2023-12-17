from flask import Flask
from flask_restx import Api, Resource, fields, reqparse
from config import Config
from sqlalchemy import exc
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
    # 'department_id': fields.Integer(description='The department ID'),
    # 'department_name': fields.String(description='The department name'),
    'department': fields.Nested(department_fields, description='The department information')
})

# Define a data model for input
put_department_parser = reqparse.RequestParser()
put_department_parser.add_argument('department_id', type=int, required=True, help='Department ID is required.')
put_department_parser.add_argument('department_name', type=str, required=True, help='Department name is required.')

# Define a data model for input
put_employee_parser = reqparse.RequestParser()
put_employee_parser.add_argument('employee_id', type=int, required=True, help='Employee ID is required.')
put_employee_parser.add_argument('employee_name', type=str, required=True, help='Employee Name is required.')
put_employee_parser.add_argument('employee_role', type=str, required=True, help='Employee Role is required.')
put_employee_parser.add_argument('employee_information', type=str, required=True, help='Employee Information is required.')
put_employee_parser.add_argument('department_id', type=int, required=True, help='Department ID required.')
put_employee_parser.add_argument('department_name', type=str, required=True, help='Department Name is required.')

@api.route('/departments')
class AllDepartmentsResource(Resource):
    @api.marshal_with(department_fields)
    def get(self):
        departments = Department.query.all()
        return [{'department_id': department.department_id, 'department_name': department.department_name} for department in departments]

# Endpoint for retrieving all employees
@api_ns.route('/employees')
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
                # 'department_id': employee.department_id,
                # 'department_name': employee.department_name
                'department': {
                    'department_id': employee.department.department_id,
                    'department_name': employee.department.department_name
                }
            }
            for employee in employees
        ]
        
    @api_ns.expect(put_employee_parser)
    @api_ns.marshal_with(employee_fields, code=201)
    def post(self):
        args = put_employee_parser.parse_args()
        employee_id = args['employee_id']
        employee_name = args['employee_name']
        employee_role = args['employee_role']
        employee_information = args['employee_information']
        department_id = args['department_id']
        department_name = args['department_name']

        # Check if the department exists
        existing_department = db.session.query(Department).filter_by(department_id=department_id).first()

        if not existing_department:
            # If the department does not exist, create it
            new_department = Department(
                department_id=department_id,
                department_name=department_name
            )
            db.session.add(new_department)
            db.session.commit()
            existing_department = new_department  # Use the newly created department

        # Corrected instantiation of the Employee instance
        new_employee = Employee(
            employee_id=employee_id,
            employee_name=employee_name,
            employee_role=employee_role,
            employee_information=employee_information,
            department_id=department_id
        )

        db.session.add(new_employee)
        db.session.commit()

        # Fetch the department information for the response
        department_info = {
            'department_id': existing_department.department_id,
            'department_name': existing_department.department_name
        }

        # Include department information in the response
        new_employee_dict = {
            'employee_id': new_employee.employee_id,
            'employee_name': new_employee.employee_name,
            'employee_role': new_employee.employee_role,
            'employee_information': new_employee.employee_information,
            'department': department_info
        }

        return new_employee_dict, 201
        


@api_ns.route('/employee/<int:id>')
class GetEmployee(Resource):
    @api_ns.marshal_with(employee_fields)
    def get(self, id):
        employee = db.session.query(Employee).filter_by(employee_id=id).first()
        if employee:
            return employee
        return {'message': 'Employee not found.'}, 404
    
    @api.expect(put_employee_parser)
    @api_ns.marshal_with(employee_fields)
    def put(self, id):
        args = put_employee_parser.parse_args()
        
        employee = db.session.query(Employee).filter_by(employee_id=id).first()
        if employee:
            employee.employee_id = args['employee_id']
            employee.employee_name = args['employee_name']
            employee.employee_role = args['employee_role']
            employee.employee_information = args['employee_information']
            
            # Update the department
            department_id = args['department_id']
            department_name = args['department_name']
            
            department = db.session.query(Department).filter_by(department_id=department_id).first()
            if department:
                department.department_name = department_name
                # Assuming you want to update the department_id in the employee as well
                employee.department_id = department_id
                db.session.commit()
                return employee
            else:
                return {'message': 'Department not found'}, 404
        else:
            return {'message': 'Employee not found'}, 404
        
    @api_ns.response(204, 'Employee and Department deleted successfully')
    def delete(self, id):
        employee = db.session.query(Employee).filter_by(employee_id=id).first()
        if employee:
            # Delete the associated department
            department = db.session.query(Department).filter_by(department_id=employee.department_id).first()
            if department:
                db.session.delete(department)

            # Delete the employee
            db.session.delete(employee)
            db.session.commit()
            return '', 204  # No content
        else:
            return {'message': 'Employee not found'}, 404
        
    # @api_ns.expect(put_employee_parser)
    # @api_ns.marshal_with(employee_fields, code=201)
    # def post(self):
    #     args = put_employee_parser.parse_args()

    #     # Create a new Employee instance
    #     new_employee = Employee(
    #         employee_id=args['employee_id'],
    #         employee_name=args['employee_name'],
    #         employee_role=args['employee_role'],
    #         employee_information=args['employee_information'],
    #         department_id=args['department_id'],
    #         department_name=args['department_name']
    #     )

    #     # Check if the department exists
    #     department_id = args['department_id']
    #     department_name = args['department_name']
    #     existing_department = db.session.query(Department).filter_by(department_id=department_id).first()

    #     if not existing_department:
    #         # If the department doesn't exist, create a new one
    #         new_department = Department(
    #             department_id=department_id,
    #             department_name=department_name
    #         )
    #         db.session.add(new_department)
    #         new_employee.department = new_department

    #     db.session.add(new_employee)
    #     db.session.commit()

    #     return new_employee, 201


@api.route('/swagger')
class SwaggerResource(Resource):
    def get(self):
        return api.swagger_ui()

if __name__ == '__main__':
    app.run(debug=True)
