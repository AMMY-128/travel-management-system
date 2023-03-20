from flask import Flask,render_template,request,session,redirect,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user,logout_user,login_manager,LoginManager
from flask_login import login_required,current_user
from flask_mail import Mail
import json



#mydatababe connection
local_server=True
app=Flask(__name__)
app.secret_key="jd"



# this is for getting unique user access
login_manager=LoginManager(app)
login_manager.login_view='login'



# SMTP MAIL SERVER SETTINGS

app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME="add your gmail-id",
    MAIL_PASSWORD="add your gmail-password"
)
mail = Mail(app)



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))




app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@localhost/store'
db=SQLAlchemy(app)


# here we will create db models that is tables


class User(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(50))
    email=db.Column(db.String(50),unique=True)
    password=db.Column(db.String(1000))


class Purchasetable(UserMixin,db.Model):
  id=db.Column(db.Integer,primary_key=True)
  ProductName=db.Column(db.String(50))
  SellerName=db.Column(db.String(50))
  BatchNumber=db.Column(db.String(50))
  Quantity=db.Column(db.Integer)
  PurchaseDate=db.Column(db.Date)
  PurchaseRate=db.Column(db.Integer)
  SellingRate=db.Column(db.Integer)
  ExpiryDate=db.Column(db.Integer)


class Inventorytable(UserMixin,db.Model):
  Id=db.Column(db.Integer,primary_key=True)
  ProductName=db.Column(db.String(50))
  BatchNumber=db.Column(db.String(50))
  Quantity=db.Column(db.String(50))
  PurchaseDate=db.Column(db.Date)
  PurchaseRate=db.Column(db.Integer)
  SellingRate=db.Column(db.Integer)
  ExpiryDate=db.Column(db.Date)
  


class Customertable(UserMixin,db.Model):
  id=db.Column(db.Integer,primary_key=True)
  CustomerName=db.Column(db.String(50))
  CustomerContact=db.Column(db.String(50))
  CustomerAddress=db.Column(db.String)  
  

class Sellertable(UserMixin,db.Model):
  id=db.Column(db.Integer,primary_key=True)
  SellerName=db.Column(db.String(50))
  SellerContact=db.Column(db.String(50))
  SellerAddress=db.Column(db.String)



class Saletable(UserMixin,db.Model):
  id=db.Column(db.Integer,primary_key=True)
  Date=db.Column(db.Date)
  Customer=db.Column(db.String(150))
  ProductName=db.Column(db.String(50))
  Quantity=db.Column(db.String(50))
  Batch=db.Column(db.String(50))
  Amount=db.Column(db.Integer)


# here we will pass endpoints and run the fuction
@app.route("/")
def mainpage():
     return render_template("home.html") 

@app.route("/home")
def home():
     return render_template("home.html") 

@app.route("/flight")
def flight():
     return render_template("flight.html") 

@app.route("/about")
def about():
     return render_template("about.html") 

@app.route("/contact")
def contact():
     return render_template("contact.html") 


@app.route('/signup',methods=['POST','GET'])
def signup():
    if request.method == "POST":
        username=request.form.get('username')
        email=request.form.get('email')
        password=request.form.get('password')
        user=User.query.filter_by(email=email).first()
        if user:
            flash("Email Already Exist","warning")
            return render_template('/signup.html')
        encpassword=generate_password_hash(password)

        new_user=db.engine.execute(f"INSERT INTO `user` (`username`,`email`,`password`) VALUES ('{username}','{email}','{encpassword}')")

        # this is method 2 to save data in db
        # newuser=User(username=username,email=email,password=encpassword)
        # db.session.add(newuser)
        # db.session.commit()
        flash("Signup Success Please Login","success")
        return render_template("login.html")

          

    return render_template('signup.html')


@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == "POST":
        email=request.form.get('email')
        password=request.form.get('password')
        user=User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password,password):
            login_user(user)
            flash("Login Success","primary")
            return redirect(url_for('Sale_counter'))
        else:
            flash("invalid credentials")
            return render_template(' login.html')





    return render_template('login.html')

                

         


@app.route("/Sale_counter",methods=['POST','GET'])
def Sale_counter():
     if request.method=="POST":
         Date=request.form.get('Date')
         ProductName=request.form.get('Product_name')
         Batch=request.form.get('Select_batch')
         Quantity=request.form.get('Quantity')
         Customer=request.form.get('Customer_name')
         Amount=request.form.get('Amount')
         query=db.engine.execute(f"INSERT INTO `saletable`(`Date`,`Customer`,`ProductName`,`Batch`,`Quantity`,`Amount`) VALUES('{Date}','{Customer}','{ProductName}','{Batch}','{Quantity}','{Amount}')")


   
     posts=db.engine.execute("SELECT * ,`Amount`*`Quantity` AS `Total_amount` FROM `saletable`")
     return render_template("Sale_counter.html",posts=posts)



@app.route("/updatesale/<string:id>",methods=['POST','GET'])
@login_required
def updatesale(id):
    posts=Saletable.query.filter_by(id=id).first()
    if request.method=="POST":
        Date=request.form.get('Date')
        ProductName=request.form.get('Product_name')
        Batch=request.form.get('Select_batch')
        Quantity=request.form.get('Quantity')
        Customer=request.form.get('Customer_name')
        Amount=request.form.get('Amount')
        db.engine.execute(f"UPDATE `saletable` SET `Date` = '{Date}', `Customer` = '{Customer}',`ProductName` = '{ProductName}',`Batch` = '{Batch}',`Quantity` = '{Quantity}',`Amount` = '{Amount}' WHERE `saletable`.`id` = {id}")
        return redirect('/Sale_counter')  
       
    return render_template("updatesale.html",post=posts)
    
    

@app.route("/delete/<string:id>",methods=['POST','GET'])
@login_required
def delete(id):
    db.engine.execute(f"DELETE FROM `saletable` WHERE `saletable`.`id`={id}")
    flash("Slot Deleted Successful","danger")
    return redirect('/Sale_counter')    

@app.route("/Purchase",methods=['POST','GET'])
@login_required
def purchase():
     if request.method=='POST':
          PurchaseDate=request.form.get('date')
          SellerName=request.form.get('Seller_name')
          BatchNumber=request.form.get('Batch_number')
          ProductName=request.form.get('Product_name')
          Quantity=request.form.get('Quantity')
          PurchaseRate=request.form.get('Purchase_rate')
          SellingRate=request.form.get('Selling_rate')
          ExpiryDate=request.form.get('Expires_on_or_before')
          query=db.engine.execute(f"INSERT INTO `purchasetable`(`ProductName`,`SellerName`,`BatchNumber`,`Quantity`,`PurchaseDate`,`PurchaseRate`,`SellingRate`,`ExpiryDate`) VALUES('{ProductName}','{SellerName}','{BatchNumber}','{Quantity}','{PurchaseDate}','{PurchaseRate}',' {SellingRate}','{ExpiryDate}')") 
    
     posts=db.engine.execute("SELECT * FROM `purchasetable`")
     
     return render_template("Purchase.html",posts=posts)      


@app.route("/updatepurchase/<string:id>",methods=['POST','GET'])
@login_required
def updatepurchase(id):
    posts=Purchasetable.query.filter_by(id=id).first()
    if request.method=="POST":
        PurchaseDate=request.form.get('date')
        SellerName=request.form.get('Seller_name')
        BatchNumber=request.form.get('Batch_number')
        ProductName=request.form.get('Product_name')
        Quantity=request.form.get('Quantity')
        PurchaseRate=request.form.get('Purchase_rate')
        SellingRate=request.form.get('Selling_rate')
        ExpiryDate=request.form.get('Expires_on_or_before')
        db.engine.execute(f"UPDATE `purchasetable` SET `ProductName` = '{ProductName}', `SellerName` = '{SellerName}',`BatchNumber` = '{BatchNumber}',`Quantity` = '{Quantity}',`PurchaseDate` = '{PurchaseDate}',`PurchaseRate` = '{PurchaseRate}',`SellingRate` = '{SellingRate}',`ExpiryDate` = '{ExpiryDate}' WHERE `purchasetable`.`id` = {id}")
        return redirect('/Purchase')  
       
    return render_template("updatepurchase.html",post=posts)
    
    

@app.route("/deletep/<string:id>",methods=['POST','GET'])
@login_required
def deletep(id):
    db.engine.execute(f"DELETE FROM `purchasetable` WHERE `purchasetable`.`id`={id}")
    flash("Slot Deleted Successful","danger")
    return redirect('/Purchase')    



@app.route("/Customer",methods=['POST','GET'])
@login_required
def customer():
      
     if request.method=="POST":
          CustomerName=request.form.get('CustomerName')
          CustomerContact=request.form.get('CustomerContact')
          CustomerAddress=request.form.get('CustomerAddress')
          db.engine.execute(f"INSERT INTO `customertable`(`CustomerName`,`CustomerContact`,`CustomerAddress`) VALUES('{CustomerName}','{CustomerContact}','{CustomerAddress}')") 
     
     posts=db.engine.execute("SELECT * FROM `customertable`")
     
    
     
     return render_template("Customer.html",posts=posts)     

@app.route("/updatecustomer/<string:id>",methods=['POST','GET'])
@login_required
def updatecustomer(id):
    posts=Customertable.query.filter_by(id=id).first()
    if request.method=="POST":
          CustomerName=request.form.get('CustomerName')
          CustomerContact=request.form.get('CustomerContact')
          CustomerAddress=request.form.get('CustomerAddress')
          db.engine.execute(f"UPDATE `customertable` SET `CustomerName` = '{CustomerName}', `CustomerContact` = '{CustomerContact}',`CustomerAddress` = '{CustomerAddress}'WHERE `customertable`.`id` = {id}")
          return redirect('/Customer')  
       
    return render_template("updatecustomer.html",post=posts)
    
    

@app.route("/deletec/<string:id>",methods=['POST','GET'])
@login_required
def deletec(id):
    db.engine.execute(f"DELETE FROM `customertable` WHERE `customertable`.`id`={id}")
    flash("Slot Deleted Successful","danger")
    return redirect('/Customer')         
     
@app.route("/Seller",methods=['POST','GET'])
@login_required
def seller():
     if request.method=="POST":
          SellerName=request.form.get('Sellers_name')
          SellerContact=request.form.get('Contact')
          SellerAddress=request.form.get('Address')
          query=db.engine.execute(f"INSERT INTO `sellertable`(`SellerName`,`SellerContact`,`SellerAddress`) VALUES('{SellerName}','{SellerContact}','{SellerAddress}')") 
       
     posts=db.engine.execute("SELECT * FROM `sellertable`")
     
     return render_template("Seller.html",posts=posts)  

@app.route("/updateseller/<string:id>",methods=['POST','GET'])
@login_required
def updateseller(id):
    posts=Sellertable.query.filter_by(id=id).first()
    if request.method=="POST":
          SellerName=request.form.get('Sellers_name')
          SellerContact=request.form.get('Contact')
          SellerAddress=request.form.get('Address')
          db.engine.execute(f"UPDATE `sellertable` SET `SellerName` = '{SellerName}', `SellerContact` = '{SellerContact}',`SellerAddress` = '{SellerAddress}'WHERE `sellertable`.`id` = {id}")
          return redirect('/Seller')  
       
    return render_template("updateseller.html",post=posts)
    
    

@app.route("/deletes/<string:id>",methods=['POST','GET'])
@login_required
def deletes(id):
    db.engine.execute(f"DELETE FROM `sellertable` WHERE `sellertable`.`id`={id}")
    flash("Slot Deleted Successful","danger")
    return redirect('/Seller')          


@app.route("/Inventory")
@login_required
def inventory():
      posts=db.engine.execute("SELECT P.`ProductName`,P.`BatchNumber`,P.`Quantity`-S.`Quantity` AS `Quantity`,P.`ExpiryDate` FROM `purchasetable` P JOIN `saletable` S ON P.`ProductName`=S.`ProductName` GROUP BY `ProductName` ")
      return render_template("Inventory.html",posts=posts)
    
         



app.run(debug=True)   