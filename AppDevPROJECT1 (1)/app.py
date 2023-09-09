from flask import Flask, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_bcrypt import Bcrypt
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from datetime import datetime
from wtforms import StringField,PasswordField,SubmitField 
from flask_login import LoginManager, UserMixin, login_user , logout_user ,login_required ,current_user
from sqlalchemy.orm import aliased


app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///grocery.sqlite3"
app.config['SECRET_KEY']='24cd789182149decb4e5bf16'
db=SQLAlchemy()
bcrypt=Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view= "user_login"

login_manager.login_message_category="info"
db.init_app(app)
app.app_context().push()



#-----------------------------------------------------------------------------------------------------------Classes--------#
@login_manager.user_loader
def load_admin(admin_id):
    return Admin.query.get(int(admin_id))

class Admin(db.Model, UserMixin):
    __tablename__="admin"
    admin_id=db.Column(db.Integer, autoincrement=True, primary_key=True)
    admin_name=db.Column(db.String,unique=True,nullable=False)
    password=db.Column(db.String,nullable=False)
    sect= db.relationship("Section",  backref='adm' ,secondary="sectioncreated")  
     
    def check_password(self, attempted_password):
        #return bcrypt.check_password_hash(self.password, attempted_password)      
        if self.password == attempted_password:
            return (attempted_password)

        
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=30), nullable=False, unique=True)
    email_address = db.Column(db.String(length=50), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)
#    product = db.relationship('Product', lazy=True)
    
    @property
    def password(self):
        return self.password
    
    @password.setter
    def password(self, plain_text_password):
        self.password_hash=bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

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
    manufacturingdate=db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    expirydate=db.Column(db.DateTime, nullable=False )
    price=db.Column(db.Integer,nullable=False)
    unit=db.Column(db.String,nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)

class Productcreated(db.Model):
    pc_id=db.Column(db.Integer, autoincrement=True, primary_key=True)
    sproduct_id=db.Column(db.Integer, db.ForeignKey("product.p_id"), nullable=False)
    csection_id=db.Column(db.Integer, db.ForeignKey("section.section_id"),nullable=False)

class Cart(db.Model):
    cart_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.p_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    user = db.relationship('User', backref=db.backref('cart_items', lazy=True))
    product = db.relationship('Product', backref=db.backref('carts', lazy=True))    

class Order(db.Model):
    order_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    total_amount= db.Column(db.Integer, nullable=False)
    product_names =db.Column(db.String, nullable=False)
    user = db.relationship('User', backref=db.backref('orders', lazy=True))
#------------------------------------------------------------------------------------------------------------Forms-----------#

class RegisterForm(FlaskForm):
    
    def validate_username(self,username_if_exists):
        user=User.query.filter_by(username=username_if_exists.data).first()
        if user:
            raise ValidationError('Sorry, This username already exists! Please try a different username')

    def validate_email_address(self,email_address_if_exists):
        email_address=User.query.filter_by(email_address=email_address_if_exists.data).first()
        if email_address:
            raise ValidationError('Sorry, This email address already exists! Please try a different email address')  
    
            
    username = StringField(label='User Name:', validators=[Length(min=2, max=25), DataRequired()])
    email_address = StringField(label='Email Address:', validators=[Email(), DataRequired()])
    password = PasswordField(label='Password:', validators=[Length(min=8), DataRequired()])
    conpassword = PasswordField(label='Confirm Password:',validators=[EqualTo('password'), DataRequired()])
    submit = SubmitField(label='Create Account')      

class UserLoginForm(FlaskForm):
    username= StringField(label='User Name:', validators=[DataRequired()])
    password= PasswordField(label='Password:', validators=[DataRequired()])
    submit= SubmitField(label='Sign in')

class AdminLoginForm(FlaskForm):
    username=StringField(label='User name:', validators=[DataRequired()])
    password=PasswordField(label='Password:', validators=[DataRequired()])
    submit= SubmitField(label='Sign in')    

#------------------------------------------------------------------------------------------------------------Routes------#

@app.route('/')
@app.route('/home', methods=["GET","POST"])
def home_page():
    return render_template('home.html') 

@app.route('/store',methods=['GET','POST'])
@login_required
def store():
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        quantity = int(request.form.get('quantity', 1))  
        product = Product.query.get(product_id)
        if product and quantity > 0:
            cart_item = Cart(user_id=current_user.id, product_id=product_id, quantity=quantity)
            db.session.add(cart_item)
            db.session.commit()
            flash(f'{quantity} {product.product_name} added to your cart!', 'success')
            return redirect(url_for('store'))
    
    section_alias = aliased(Section)
    productcreated_alias = aliased(Productcreated)
    product_alias = aliased(Product)
    result = db.session.query(
        section_alias.section_id,
        section_alias.section_name,
        section_alias.category,
        product_alias.p_id,
        product_alias.product_name,
        product_alias.manufacturingdate,
        product_alias.expirydate,
        product_alias.price,
        product_alias.unit,
        product_alias.quantity
    ).join(
        productcreated_alias,
        productcreated_alias.csection_id == section_alias.section_id
    ).join(
        product_alias,
        productcreated_alias.sproduct_id == product_alias.p_id
    ).all()
    return render_template('store.html', products=result)
#----USER----------------------------------------------------------------------------------------------------------------------------------------
@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        create_user = User(username=form.username.data,
                              email_address=form.email_address.data,
                              password=form.password.data)
        db.session.add(create_user)
        db.session.commit()
        login_user(create_user)
        flash(f'Account created successfully! You are now logged in as {create_user.username}', category='success')
        return redirect(url_for('store'))
    if form.errors != {}: 
        for err_msg in form.errors.values():
            flash(f'Opps..We encountered some error while creating your account: {err_msg}', category='danger')

    return render_template('register_page.html', form=form)

@app.route('/login', methods=['GET','POST'])
def user_login():
    form = UserLoginForm()
    if form.validate_on_submit():
        attempted_user= User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
            attempted_password=form.password.data):
            login_user(attempted_user)
            flash(f'Yaay..You are now logged in as {attempted_user.username}', category='success')
            return redirect(url_for('store'))
        else:
            flash('Please try again.The username and the password are not matching.', category='danger')

    return render_template('user_login.html', form=form)

@app.route('/user_logout',methods=['GET','POST'])
def user_logout():
    logout_user()
    flash('Your have been logged out!',category= 'info')
    return render_template('home.html')

@app.route('/user_profile',methods=['GET','POST'] )
@login_required
def user_profile():
    user_id = current_user.id
    orders = Order.query.filter_by(user_id=user_id).all()
    return render_template('userprofile.html',orders=orders)
    
    
#-----ADMIN------------------------------------------------------------------------------------------------------------------------------------
@app.route('/adminlogin', methods=['GET','POST'])
def adminlogin():
    form = AdminLoginForm()
    if form.validate_on_submit():
        attempted_admin= Admin.query.filter_by(admin_name=form.username.data).first()
        if attempted_admin and attempted_admin.check_password(
            attempted_password=form.password.data):
            id=attempted_admin.admin_id
            return redirect(url_for('admindashboard',id=id))
           
        else:
            flash('Please try again.The username and the password are not matching.', category='danger')
    return render_template('adminlogin.html', form=form)

@app.route('/admin_logout',methods=['GET','POST'])
def admin_logout():
    logout_user()
    flash('Your have been logged out!',category= 'info')
    return render_template('home.html')

@app.route('/admin/<id>')
def admindashboard(id):
    if request.method=='GET':
        ad=Admin.query.filter_by(admin_id=id).first()
        sec=ad.sect
        d={}
        plist=[]
        for i in sec:
            prod=i.product
            plist.append(prod)
        for i in range(len(sec)):
            d[sec[i]]=plist[i]
        print(d)
        return render_template('admindashboard.html',sec=d,id=id)

#--Section -------------------------------------------------------------------------------------------------------   
@app.route('/section/create/<id>', methods=['GET','POST'])
def sectioncreate(id):
    if request.method=='GET':
        return render_template('sectioncreate.html',id=id)
    if request.method =='POST':
        section_name=request.form['section_name']
        category=request.form['category']
        section_created=Section(section_name=section_name,category=category)
        db.session.add(section_created)
        db.session.commit()
        sec_id=section_created.section_id
        admin_section=Sectioncreated(screate_admin_id=id,csection_id=sec_id)
        db.session.add(admin_section)
        db.session.commit()
        return redirect(url_for('admindashboard', id=id))
    
@app.route("/section/edit/<id>/<s_id>", methods=['GET','POST'])
def sectionedit(id,s_id):
    if request.method=='GET':
        return render_template('sectionedit.html',s_id=s_id,id=id)
    if request.method =='POST':
        section_name=request.form['section_name']
        category=request.form['category']
        sec=Section.query.filter_by(section_id=s_id).update({"section_name":section_name})
        db.session.commit()
        return redirect(url_for('admindashboard', id=id))
    
@app.route('/section/delete/<id>/<s_id>')
def sectiondelete(id,s_id):
    sec=Section.query.filter_by(section_id=s_id).first()
    prod=sec.product
    for i in prod:
        db.session.delete(i)
    Productcreated.query.filter_by(csection_id=s_id).delete()
    Sectioncreated.query.filter_by(csection_id=s_id).delete()
    Section.query.filter_by(section_id=s_id).delete()
    db.session.commit()
    return redirect(url_for('admindashboard', id=id))

#--Product-----------------------------------------------------------------------------------------
@app.route('/product/create/<id>/<s_id>', methods=['GET','POST'])
def productcreate(id,s_id):
    if request.method=='GET':
        return render_template('productform.html',s_id=s_id,id=id)
    if request.method=='POST':
        pname=request.form['pname']
        mdate=request.form['mdate']
        unit=request.form['price_per']
        quantity=request.form['quantity']
#        m_value = datetime.strptime(str(mdate), '%Y-%m-%dT%H:%M')
#        edate=request.form['edate']
        mdate = request.form['mdate']
        m_value = datetime.strptime(mdate, '%Y-%m-%d')
        edate = request.form['edate']
        e_value = datetime.strptime(edate, '%Y-%m-%d')
#        e_value = datetime.strptime(str(edate), '%Y-%m-%dT%H:%M')
        price=request.form['price']
        section = Section.query.get(s_id)
        if not section:
            flash('Section not found.', category='danger')
            return redirect(url_for('admindashboard', id=current_user.admin_id))
        product=Product(product_name=pname, manufacturingdate=m_value, expirydate=e_value, price=price, quantity=quantity, unit=unit)
#        product.admin=current_user
#        section.product.append(product)
        db.session.add(product)
        db.session.commit()
        pid=product.p_id
        proc=Productcreated(sproduct_id=pid,csection_id=s_id)
        db.session.add(proc)
        db.session.commit()
        return redirect(url_for('admindashboard', id=id))
    
@app.route("/product/edit/<p_id>/section/<s_id>/<id>",methods=['GET','POST'])
def edit_product(p_id,s_id,id):
    product_to_edit = Product.query.filter_by(p_id=p_id).first()
    if request.method == 'POST':
        product_to_edit.product_name = request.form['pname']
        product_to_edit.price = request.form['price']
        product_to_edit.unit = request.form['price_per']
        product_to_edit.quantity = request.form['quantity']
        db.session.commit()
        return redirect(url_for('admindashboard', id=id))
    return render_template('edit_product.html', product=product_to_edit,id=id,s_id=s_id)       

@app.route("/product/delete/<int:p_id>/section/<int:section_id>/<int:id>", methods=['GET','POST'])
def delete_product(p_id,id,section_id):    
    Productcreated.query.filter_by(sproduct_id=p_id).delete()
    Product.query.filter_by(p_id=p_id).delete()
    db.session.commit()
    return redirect(url_for('admindashboard', id=id))
#------CART------------------------------------------------------------------------------------------------------------------------------
@app.route('/add_to_cart/<p_id>/<s_id>', methods=['POST'])
@login_required
def add_to_cart(p_id,s_id):
    product = Product.query.get(p_id)
    userid=current_user.id
    if product:
        if product.quantity > 0:
            user_cart = Cart.query.filter_by(user_id=userid, product=p_id).first() 
            if user_cart:
                user_cart.quantity += 1
            else:
                user_cart = Cart(user=current_user, product=product)
            db.session.add(user_cart)
            db.session.commit()
            flash('Product added to cart successfully.', category='success')
        else: 
            flash('Sorry,Product is out of stock.', category='danger')    
    else:
        flash('Product not found.', category='danger')
    return redirect(url_for('store'))

@app.route('/remove_from_cart/<int:cart_item_id>', methods=['POST'])
@login_required
def remove_from_cart(cart_item_id):
    cart_item = Cart.query.get_or_404(cart_item_id)
    db.session.delete(cart_item)
    db.session.commit()
    flash('Product removed from cart!', 'info')
    return redirect(url_for('store'))
#-----ORDER------------------------------------------------------------------------------------------------------------------------
@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if request.method == 'POST':

        total_amount = 0
        for cart_item in current_user.cart_items:
            total_amount += cart_item.product.price * cart_item.quantity

        return render_template('payment.html', total_amount=total_amount)

    return redirect(url_for('store'))

@app.route('/place_order', methods=['POST'])
@login_required
def place_order():
    if current_user.cart_items:

        total_amount = 0
        product_names = []  

        for cart_item in current_user.cart_items:
            total_amount += cart_item.product.price * cart_item.quantity
            product_names.append(cart_item.product.product_name)

        order = Order(user_id=current_user.id, total_amount=total_amount, product_names=", ".join(product_names))
        db.session.add(order)

        for cart_item in current_user.cart_items:
            product = cart_item.product
            if product.quantity >= cart_item.quantity:
                product.quantity -= cart_item.quantity
                cart_item.order = order
            else:
                flash(f'Not enough stock for {product.product_name}. Remove from cart.', category='danger')
                return redirect(url_for('store'))
        cart_item = Cart.query.all()
        for i in cart_item:
            db.session.delete(i)
        db.session.commit()
        flash(f'Congratulations, order placed successfully! Total amount: Rs.{total_amount}', category='success')
    else:
        flash('Your cart is empty. Add something to your cart to proceed with the order.', 'info')

    return redirect(url_for('store'))
#----SEARCH----------------------------------------------------------------------------------------------------------------------------
@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():

    if request.method == 'POST':
        searched_word = request.form['searched_word']

        section_alias = aliased(Section)
        productcreated_alias = aliased(Productcreated)
        product_alias = aliased(Product)
        result = db.session.query(
            section_alias.section_id,
            section_alias.section_name,
            section_alias.category,
            product_alias.p_id,
            product_alias.product_name,
            product_alias.manufacturingdate,
            product_alias.expirydate,
            product_alias.price,
            product_alias.unit,
            product_alias.quantity
        ).join(
            productcreated_alias,
            productcreated_alias.csection_id == section_alias.section_id
        ).join(
            product_alias,
            productcreated_alias.sproduct_id == product_alias.p_id
        ).all()

        products=[]
        for i in result:
            product_name = i.product_name.lower()
            category = i.category.lower()
            section_name = i.section_name.lower()
            
            if (
                product_name == searched_word.lower()
                or category == searched_word.lower()
                or section_name == searched_word.lower()
            ):
                products.append(i)

        try:
            price_searched = float(searched_word)
            products=[]
            for i in result:
                if i.price==price_searched:
                    products.append(i)
        except ValueError:
            pass

        products = list(set(products))
        if products ==[]:
            flash('Sorry, no product matches your search', category='danger')
        return render_template('store.html', products=products)

    return redirect(url_for('store'))
    

if __name__=="__main__":
    db.create_all()
    app.run(debug=True, port=8080)
