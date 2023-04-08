from datetime import datetime
from galleryapp import db

class Admin(db.Model):
    admin_id=db.Column(db.Integer,autoincrement=True,primary_key=True)
    admin_username=db.Column(db.String(100),nullable=False,unique=True)
    admin_password=db.Column(db.String(20),nullable=False)

class User(db.Model):
    user_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    user_username=db.Column(db.String(20),nullable=False,unique=True)
    user_fname = db.Column(db.String(50),nullable=False)
    user_lname = db.Column(db.String(50),nullable=False)
    user_email = db.Column(db.String(100),nullable=False,unique=True)
    user_pwd = db.Column(db.String(120),nullable=False)
    user_bio = db.Column(db.Text(),nullable=True)
    user_phone=db.Column(db.String(120),nullable=True)
    user_pix = db.Column(db.String(120),nullable=True)
    user_dob = db.Column(db.Date,nullable=True)
    user_datereg=db.Column(db.DateTime(),default=datetime.utcnow)
    user_address=db.Column(db.Text(),nullable=True)
    #set the foreign key
    #set relationship
    mytrans = db.relationship("Payment", back_populates="transby")
    myorders=db.relationship("Orders",back_populates="orderby")
    myuploads =db.relationship("Artworks",back_populates="uploadedby")
    #mycomments = db.relationship("Comments", back_populates="commentby")

class Galleries(db.Model):
    gallery_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    gallery_name = db.Column(db.String(100),nullable=False)
    gallery_number=db.Column(db.String(20),nullable=True)
    gallery_email = db.Column(db.String(100),nullable=False,unique=True)
    gallery_address=db.Column(db.String(150),nullable=True)
    gallery_password=db.Column(db.String(100),nullable=False)
    #relationship with table
    mygaluploads = db.relationship("Artworks",back_populates="uploadedgalby")


class Artworks(db.Model):
    art_id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    art_title = db.Column(db.String(100),nullable=False)
    art_year = db.Column(db.String(10),nullable=False)
    artist_fullname = db.Column(db.String(120),nullable=False)
    art_pix = db.Column(db.String(120),nullable=True)
    art_dimension = db.Column(db.String(20),nullable=False)
    art_price = db.Column(db.Float(),nullable = False)
    art_status= db.Column(db.Enum('1','0'),nullable = False,server_default=('0'))
    art_availablestatus= db.Column(db.Enum('1','0'),nullable = False,server_default=('1'))
    art_categoryid= db.Column(db.Integer,db.ForeignKey('category.category_id'),nullable=False)
    art_mediumid=db.Column(db.Integer,db.ForeignKey('medium.medium_id'),nullable=True)
    art_subjectid=db.Column(db.Integer,db.ForeignKey('subject.subject_id'),nullable=True)
    art_materialid=db.Column(db.Integer,db.ForeignKey('material.material_id'),nullable=True)
    art_styleid=db.Column(db.Integer,db.ForeignKey('style.style_id'),nullable=True)
    upload_userid= db.Column(db.Integer,db.ForeignKey('user.user_id'),nullable=False)
    upload_galleryid = db.Column(db.Integer,db.ForeignKey('galleries.gallery_id'),nullable=False,)
    upload_date = db.Column(db.DateTime(),default=datetime.utcnow)
    #relationship with other tables
    uploadedby=db.relationship("User",back_populates="myuploads")
    uploadedgalby=db.relationship("Galleries",back_populates="mygaluploads")
    the_orders=db.relationship("Order_details",back_populates="art")

class Orders(db.Model):
    order_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    order_amt =db.Column(db.Float(2),nullable=False)
    order_date = db.Column(db.DateTime(),default=datetime.utcnow)
    order_status=db.Column(db.Enum('pending','failed','success'),nullable=False,server_default=('pending'))
    order_userid =db.Column(db.Integer,db.ForeignKey('user.user_id'),nullable=False)
    order_address= db.Column(db.Text(),nullable=True)
    order_phone=db.Column(db.String(20),nullable=True)
    #relationship with state table
    orderby = db.relationship("User",back_populates="myorders")
    order_deets=db.relationship("Order_details",back_populates="the_order")
    #state_deets = db.relationship("State", back_populates="lgas")

class Order_details(db.Model):
    orderdetails_id = db.Column(db.Integer,primary_key=True)
    orderdetails_orderid = db.Column(db.Integer,db.ForeignKey('orders.order_id'),nullable=False)
    orderdetails_amt = db.Column(db.Float(2),nullable=False)
    orderdetails_artid = db.Column(db.Integer,db.ForeignKey('artworks.art_id'),nullable=False)
    #relationship with order table
    the_order=db.relationship("Orders",back_populates="order_deets")
    art=db.relationship("Artworks",back_populates="the_orders")

class Payment(db.Model):
    payment_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    payment_amt = db.Column(db.Float(2),nullable=True)
    payment_status = db.Column(db.Enum('pending','Failed','success'),nullable=False)
    payment_userid = db.Column(db.Integer,db.ForeignKey('user.user_id'),nullable=False)
    payment_orderid = db.Column(db.Integer,db.ForeignKey('orders.order_id'),nullable=False)
    payment_date = db.Column(db.DateTime(),default=datetime.utcnow, nullable=False)
    payment_refno=db.Column(db.Integer,nullable=False)
    payment_others=db.Column(db.Text(),nullable=True)
    #relationship with user table
    transby = db.relationship("User",back_populates="mytrans")
    # commentby = db.relationship("User", back_populates="mycomments")
    # #relationship with topics table
    # the_topic = db.relationship("Topics", back_populates="all_comments")

class Category(db.Model):
    category_id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    category_name =db.Column(db.String(100),nullable=False,unique=True)
    art_ref = db.relationship("Artworks", backref="cat")

class Messages(db.Model):
    msg_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    msg_email= db.Column(db.String(100), nullable=False)
    msg_content = db.Column(db.Text(),nullable=False)
    msg_date = db.Column(db.DateTime(),default=datetime.utcnow)

class Favorites(db.Model):
    fav_id=db.Column(db.Integer, autoincrement=True,primary_key=True)
    fav_userid=db.Column(db.Integer,db.ForeignKey('user.user_id'),nullable=False,)
    fav_artid=db.Column(db.Integer,db.ForeignKey('artworks.art_id'),nullable=False)
    art_ref = db.relationship("Artworks", backref="fav")

class Cart(db.Model):
    cart_id=db.Column(db.Integer, autoincrement=True,primary_key=True)
    cart_userid=db.Column(db.Integer,db.ForeignKey('user.user_id'),nullable=False,)
    cart_artid=db.Column(db.Integer,db.ForeignKey('artworks.art_id'),nullable=False)
    cart_itemprice = db.Column(db.Float(),nullable=False)
    cart_art = db.relationship("Artworks", backref="cart_ref")

class Medium(db.Model):
    medium_id=db.Column(db.Integer, autoincrement=True,primary_key=True)
    medium_name=db.Column(db.String(100),nullable=False,unique=True)
    art_ref = db.relationship("Artworks", backref="med")

class Subject(db.Model):
    subject_id=db.Column(db.Integer, autoincrement=True,primary_key=True)
    subject_name=db.Column(db.String(100),nullable=False,unique=True)
    art_ref = db.relationship("Artworks", backref="sub")

class Material(db.Model):
    material_id=db.Column(db.Integer, autoincrement=True,primary_key=True)
    material_name=db.Column(db.String(100),nullable=False,unique=True)
    art_ref = db.relationship("Artworks", backref="mat")

class Style(db.Model):
    style_id=db.Column(db.Integer, autoincrement=True,primary_key=True)
    style_name=db.Column(db.String(100),nullable=False,unique=True)
    art_ref = db.relationship("Artworks", backref="style")

class Product_category(db.Model):
    pc_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    product_id=db.Column(db.Integer,db.ForeignKey('artworks.art_id') ,)
    category_id=db.Column(db.Integer,db.ForeignKey('category.category_id') ,)
    medium_id=db.Column(db.Integer,db.ForeignKey('medium.medium_id') ,)
    subject_id=db.Column(db.Integer,db.ForeignKey('subject.subject_id') ,)
    style_id=db.Column(db.Integer,db.ForeignKey('style.style_id') ,)
    material_id=db.Column(db.Integer,db.ForeignKey('material.material_id'),)
    
class Newsletter(db.Model):
    news_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    email = db.Column(db.String(100),nullable=False,unique=True)