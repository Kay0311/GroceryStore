from flask import Flask, make_response
from flask_restful import Resource, Api, fields, marshal_with, reqparse
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import HTTPException
import json
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import or_


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///grocery.sqlite3'
db = SQLAlchemy()
db.init_app(app)
app.app_context().push()
api = Api(app)
CORS(app)

class Admin(db.Model):
    __tablename__="admin"
    admin_id=db.Column(db.Integer, autoincrement=True, primary_key=True)
    admin_name=db.Column(db.String,unique=True,nullable=False)
    password=db.Column(db.String,nullable=False)
    sect= db.relationship("Section",  backref='adm' ,secondary="sectioncreated")  

class Section(db.Model):
    section_id=db.Column(db.Integer, autoincrement=True, primary_key=True)
    section_name=db.Column(db.String,nullable=False)
    product=db.relationship('Product', secondary='productcreated')
    category=db.Column(db.String, nullable=False)

class Sectioncreated(db.Model):
    screate_id=db.Column(db.Integer, autoincrement=True, primary_key=True) 
    screate_admin_id=db.Column(db.Integer, db.ForeignKey("admin.admin_id"), nullable=False)
    csection_id=db.Column(db.Integer, db.ForeignKey("section.section_id"),nullable=False)
    
class Product(db.Model):
    p_id=db.Column(db.Integer, autoincrement=True, primary_key=True)
    product_name=db.Column(db.String,nullable=False)
    manufacturingdate=db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    expirydate=db.Column(db.DateTime, nullable=False )
    price=db.Column(db.Integer,nullable=False)
    unit=db.Column(db.String,nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)

class Productcreated(db.Model):
    pc_id=db.Column(db.Integer, autoincrement=True, primary_key=True)
    sproduct_id=db.Column(db.Integer, db.ForeignKey("product.p_id"), nullable=False)
    csection_id=db.Column(db.Integer, db.ForeignKey("section.section_id"),nullable=False)

class User(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=30), nullable=False, unique=True)
    email_address = db.Column(db.String(length=50), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)

#------------------------------------------------------------------------------------------------------------------------------------------------------

class NotFoundError(HTTPException):
    def __init__(self, status_code, message=''):
        self.response = make_response(message, status_code)

class NotGivenError(HTTPException):
    def __init__(self, status_code, error_code, error_message):
        message = {"error_code": error_code, "error_message": error_message}
        self.response = make_response(json.dumps(message), status_code)

#--------------------------------------------------------------------------------------------------------------------------------------------------------
section_fields={
    "section_id":fields.Integer,
    "section_name":fields.String,
    "category":fields.String

}


section_parse = reqparse.RequestParser()
section_parse.add_argument("section_name")
section_parse.add_argument("category")


class SectionAPI(Resource):
    @marshal_with(section_fields)
    def get(self,s_id):
        sec=Section.query.filter_by(section_id=s_id).first()

        if sec:
            return sec
        else:
            raise NotFoundError(status_code=404)
        
    @marshal_with(section_fields)   
    def put(self,s_id):
        sec=Section.query.filter_by(section_id=s_id).first()

        if sec is None:
            raise NotFoundError(status_code=404)
        
        args =section_parse.parse_args()
        section_name = args.get("section_name", None)
        category = args.get("category", None)

        if section_name is None:
            raise NotGivenError(status_code=400, error_code="SECTION001", error_message="Section Name is required")
        if category is None:
            raise NotGivenError(status_code=400, error_code="SECTION002", error_message="Category is required")
        
        else:
            sec.section_name=section_name
            sec.category=category
            db.session.commit()
            return sec,201
        
    @marshal_with(section_fields)   
    def post(self):
        args =section_parse.parse_args()
        section_name = args.get("section_name", None)
        category = args.get("category", None)

        if section_name is None:
            raise NotGivenError(status_code=400, error_code="SECTION001", error_message="Section Name is required")
        if category is None:
            raise NotGivenError(status_code=400, error_code="SECTION002", error_message="Category is required")
        
        else:
            sec=Section(section_name=section_name,category=category)
            db.session.add(sec)
            db.session.commit()
            return sec,201
        

    def delete(self,s_id):
        sec=Section.query.filter_by(section_id=s_id).first()

        if sec is None:
            raise NotFoundError(status_code=404)
        else:
            prod=sec.product
            for i in prod:
                db.session.delete(i)
            Productcreated.query.filter_by(csection_id=s_id).delete()
            Sectioncreated.query.filter_by(csection_id=s_id).delete()
            Section.query.filter_by(section_id=s_id).delete()
            db.session.commit()
            return 200
#--------------------------------------------------------------------------------------------------------------------------------------------------

product_fields={
    "p_id":fields.Integer,
    "product_name":fields.String,
    "manufacturingdate":fields.DateTime,
    "expirydate":fields.DateTime,
    "price": fields.Integer,
    "unit": fields.String,
    "quantity": fields.Integer
}
product_parse = reqparse.RequestParser()
product_parse.add_argument("product_name")
product_parse.add_argument("manufacturingdate")
product_parse.add_argument("expirydate")
product_parse.add_argument("price")
product_parse.add_argument("unit")
product_parse.add_argument("quantity")

class ProductAPI(Resource):

    @marshal_with(product_fields)
    def get(self, p_id):
        prod = Product.query.filter(Product.p_id == p_id).first()

        if prod:
            return prod
        else:
            raise NotFoundError(status_code=404)
   
    @marshal_with(product_fields)
    def put(self, p_id):
       
        prod = Product.query.filter(Product.p_id == p_id).first()

        if prod is None:
            raise NotFoundError(status_code=404)
        
       
        args =product_parse.parse_args()
        product_name = args.get("product_name", None)
        price = args.get("price", None)
        unit = args.get("unit", None)
        quantity = args.get("quantity", None)
        if product_name is None:
            raise NotGivenError(status_code=400, error_code="PROD001", error_message="Product Name is required")
        
        if price is None:
            raise NotGivenError(status_code=400, error_code="PROD004", error_message="price is required")
        
        if unit is None:
            raise NotGivenError(status_code=400, error_code="PROD005", error_message="unit is required")
        
        if quantity is None:
            raise NotGivenError(status_code=400, error_code="PROD006", error_message="quantity is required")
        else:
            prod.product_name = product_name
            prod.price = price
            prod.unit = unit
            prod.quantity = quantity
            db.session.commit()
            return prod,201
        

    
    def delete(self, p_id):
        
        prod = Product.query.filter(Product.p_id == p_id).scalar()
        pro = Productcreated.query.filter_by(sproduct_id=p_id).scalar()


        if prod is None or pro is None:
            raise NotFoundError(status_code=404)

        try:
            db.session.delete(prod)
            db.session.delete(pro)
            db.session.commit()
            return "successfully deleted", 200
        except Exception as e:
            db.session.rollback()
            return f"Error deleting product: {str(e)}", 500
        
    def post(self,s_id):
        
        args =product_parse.parse_args()
        product_name = args.get("product_name", None)
        mdate = args.get("manufacturingdate", None)
        edate = args.get("expirydate", None)
        price = args.get("price", None)
        unit = args.get("unit", None)
        quantity = args.get("quantity", None)
        
    
        if product_name is None:
            raise NotGivenError(status_code=400, error_code="PROD001", error_message="Product Name is required")
        
        
        if mdate is None:
            raise NotGivenError(status_code=400, error_code="PROD002", error_message="manufacturing date is required")
        
        if edate is None:
            raise NotGivenError(status_code=400, error_code="PROD003", error_message="expiry date is required")
        
        if price is None:
            raise NotGivenError(status_code=400, error_code="PROD004", error_message="price is required")
        
        if unit is None:
            raise NotGivenError(status_code=400, error_code="PROD005", error_message="unit is required")
        
        if quantity is None:
            raise NotGivenError(status_code=400, error_code="PROD006", error_message="quantity is required")
        
        
        m_value = datetime.strptime(mdate, '%Y-%m-%d')
        e_value = datetime.strptime(edate, '%Y-%m-%d')

        product = Product(
            product_name=product_name,
            manufacturingdate=m_value,
            expirydate=e_value,
            price=price,
            unit=unit,
            quantity=quantity
        )

        db.session.add(product)
        db.session.commit()

        proc = Productcreated(sproduct_id=product.p_id, csection_id=s_id)
        db.session.add(proc)
        db.session.commit()

        return product,201
#-----User-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
user_fields = {
    "id": fields.Integer,
    "username": fields.String,
    "email_address": fields.String,
    "password_hash": fields.String
}

user_parse = reqparse.RequestParser()
user_parse.add_argument("username")
user_parse.add_argument("email_address")
user_parse.add_argument("password_hash")

class UserAPI(Resource):

    @marshal_with(user_fields)
    def get(self,user_id):
        user=User.query.filter_by(id=user_id).first()
        if user:
            return user
        else:
            raise NotFoundError(status_code=404)
        
    @marshal_with(user_fields)
    def put(self,user_id):
        args = user_parse.parse_args()
        username=args.get("username")
        email_address=args.get("email_address")
        pswd=args.get("password_hash")
        

        users=User.query.filter(or_(User.user_name==username,User.email_address==email_address)).first()
        
        if username is None:
            raise NotGivenError(status_code=400, error_code="USER001", error_message="Username is required")

        if email_address is None:
            raise NotGivenError(status_code=400, error_code="USER002", error_message="Email address is required")

        if pswd is None:
            raise NotGivenError(status_code=400, error_code="USER003", error_message="Password is required")
        
        if users:
            raise NotGivenError(status_code=400, error_code="USER004", error_message="User_name or email_address already exist")
        
        use=User.query.filter_by(id=user_id).first()
        if use:
            use.username=username
            use.email_address=email_address
            use.password_hash=pswd
            db.session.commit()
            return use, 200
        
        else:
            raise NotFoundError(status_code=404)
        
    @marshal_with(user_fields)
    def post(self):
        args = user_parse.parse_args()
        username=args.get("username")
        email_address=args.get("email_address")
        pswd=args.get("password_hash")

        if username is None:
            raise NotGivenError(status_code=400, error_code="USER001", error_message="User Name is required")

        if email_address is None:
            raise NotGivenError(status_code=400, error_code="USER002", error_message="Email Address is required")

        if pswd is None:
            raise NotGivenError(status_code=400, error_code="USER003", error_message="Password is required")
        
        use=User.query.filter(or_(User.username==username,User.email_address==email_address)).first()
        if use:
            raise NotFoundError(status_code=409)

        
        else:
            use=User(user_name=username,email_address=email_address,password=pswd)
            db.session.add(use)
            db.session.commit()
            return use, 201
#------Admin--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
admin_fields = {
    "admin_id": fields.Integer,
    "admin_name": fields.String,
    "password": fields.String
}
admin_parse = reqparse.RequestParser()
admin_parse.add_argument("admin_id")
admin_parse.add_argument("admin_name")
admin_parse.add_argument("password")

class AdminAPI(Resource):

    @marshal_with(admin_fields)
    def get (self,admin_id):
        admin=Admin.query.filter_by(admin_id=admin_id).first()
        if admin:
            return admin
        else:
            raise NotFoundError(status_code=404)
        
    @marshal_with(admin_fields)
    def post(self):
        args = admin_parse.parse_args()
        admin_name=args.get("admin_name")
        passw=args.get("password")

        

        if admin_name is None:
            raise NotGivenError(status_code=400, error_code="ADMIN001", error_message="Admin_name is required")

        if passw is None:
            raise NotGivenError(status_code=400, error_code="ADMIN002", error_message="Password is required")
        

        
        ad=Admin.query.filter(or_(Admin.admin_name==admin_name)).first()

        if ad:
            raise NotFoundError(status_code=409)

        
        else:
            ad=Admin(admin_name=admin_name,password=passw)
            db.session.add(ad)
            db.session.commit()
            return ad, 200
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
api.add_resource(SectionAPI, "/api/section/<int:s_id>", "/api/section")
api.add_resource(ProductAPI, "/api/product/<int:p_id>/", "/api/product/create/<int:s_id>")
api.add_resource(UserAPI, "/api/user/<int:user_id>", "/api/user")
api.add_resource(AdminAPI, "/api/admin/<int:admin_id>","/api/admin")


if __name__=="__main__":
    db.create_all()
    app.run(debug=True, port=8080)