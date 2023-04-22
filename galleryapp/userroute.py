#import 3rd party
import os,random,string,json,requests,re
from flask import render_template,request,redirect,flash,session,url_for,jsonify
from  sqlalchemy.sql.expression import func, select
from sqlalchemy import or_
#import from local files
from werkzeug.security import generate_password_hash,check_password_hash
from galleryapp import app,db,csrf
from galleryapp.models import User,Category,Artworks,Messages,Favorites,Cart,Medium,Style,Material,Subject,Orders,Order_details,Payment,Newsletter,Product_category
from galleryapp.forms import ContactForm

#put in every route that extends template
# id = session['user']
# deets = db.session.query(User).get(id)
# deets=deets


def is_valid_email(email):
    """
    This function takes an email address as input and returns True if it is a valid email, False otherwise.
    """
    # Regular expression pattern to match an email address
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    # Use the match() method of the re module to check if the email address matches the pattern
    if re.match(pattern, email):
        return True
    else:
        return False

def generate_name():
    filename= random.sample(string.ascii_lowercase,10)#will always return a list
    return ''.join(filename)#join avery member of the list filename together

def qry():
    cart_items = db.session.query(Cart).filter(User.user_id==Cart.cart_userid).all()

@app.route('/')
def home():
    id = session.get('user')
    if id:
        deets = db.session.query(User).get(id)
        cart_items = db.session.query(Cart).filter(User.user_id==Cart.cart_userid).all()
        cat = db.session.query(Category).order_by(Category.category_name.asc()).all()
        all_arts= db.session.query(Artworks).order_by(func.rand()).limit(4).all()
        return render_template('/user/index.html',all_arts=all_arts,deets=deets,cart_items=cart_items,cat=cat)
    else:
        all_arts= db.session.query(Artworks).order_by(func.rand()).limit(4).all()
        return render_template('/user/index.html',all_arts=all_arts)

@app.route('/signup',methods=['GET','POST'])
def user_signup():
    if request.method == 'GET':
        return render_template('user/signup.html')
    else:
        emails=[]
        mails=db.session.query(User.user_email).all()
        unames=[]
        username=db.session.query(User.user_username).all()
        for i in username:
            unames.append(i[0])
        for j in mails:
            emails.append(j[0])
        #form was submited
        uname=request.form.get('username')
        fname= request.form.get('fname')
        lname= request.form.get('lname')
        email= request.form.get('email')
        phone= request.form.get('phone')
        pwd= request.form.get('password')
        chkpwd= request.form.get('chk-password')
        hashed_pwd = generate_password_hash(pwd)
        if uname!=None and fname!=None and lname!=None and email!=None and pwd!=None and pwd!=None and pwd==chkpwd:
            duplicate_username = unames.count(str(uname))
            if duplicate_username > 0:
                return 'username already exists'
            else:
                duplicate_email = emails.count(str(email))
                if duplicate_email > 0:
                    return 'email already registered'
                else:
                    #
                    #if all requirements are met, then you insert into database
                    u=User(user_username=uname,user_fname=fname,user_lname=lname,user_email=email,user_pwd=hashed_pwd,user_phone=phone)
                    #Then you add your inputs to session
                    db.session.add(u)
                    db.session.commit()
                    #then get the id of the inserted record to confirm insertion
                    userid=u.user_id
                    #then put that id in a session
                    session['user']=userid
                    return jsonify(redirect=url_for('user_login'))
        else:
            flash('all required fields to successfully signup')
            return jsonify(redirect=url_for('user_signup'))

@app.route('/check_username', methods=['POST'])
@csrf.exempt
def check_username():
    usname = request.form.get('uname')
    if usname != None:
        exists = db.session.query(User).filter(User.user_username==usname).scalar() is not None
        return str(exists)
    else:
        return "Enter Username"

@app.route('/check_email', methods=['POST'])
@csrf.exempt
def check_email():
    email = request.form.get('email')
    if email != None:
        exists = db.session.query(User).filter(User.user_email==email).scalar() is not None
        return str(exists)
    else:
        return "Enter Username"

@app.route('/login',methods=['GET','POST'])
def user_login():
    if session.get('user')!= None:
        return redirect(url_for('home'))
    else:
        if request.method=='GET':
            return render_template('user/login.html')
        else:
            uname= request.form.get('username')
            pwd= request.form.get('password')
            uobj=db.session.query(User).filter(User.user_username==uname).first()
            if uobj!= None:
                db_pwd = uobj.user_pwd
                chk = check_password_hash(db_pwd,pwd)
                if chk:
                    id = uobj.user_id
                    session['user']=id
                    return redirect(url_for('home'))
                else:
                    flash('invalid credentials')
                    return redirect(url_for('user_login'))
            else:
                flash('invalid credentials')
                return redirect(url_for('user_login'))

@app.route('/logout')
def user_logout():
    if session.get('user') !=None:
        session.pop('user',None)
    return redirect('/')

@app.route('/profile')
def profile():
    if session.get('user') == None:
        return redirect('/login')
    else:
        id = session.get('user')
        deets = db.session.query(User).get(id)
        cat = db.session.query(Category).order_by(Category.category_name.asc()).all()
        fav=db.session.query(Favorites).filter(Favorites.fav_userid==id).limit(3).all()
        cart_items = db.session.query(Cart).filter(User.user_id==Cart.cart_userid).all()
        myworks= db.session.query(Artworks).filter(Artworks.upload_userid==id).all()
        return render_template('user/profile.html',myworks=myworks,deets=deets,fav=fav,cart_items=cart_items,cat=cat)

@app.route('/account',methods=['GET','POST'])
def account():
    if request.method == 'GET':
        id = session.get('user')
        deets=db.session.query(User).filter(User.user_id==id).first()
        cat = db.session.query(Category).order_by(Category.category_name.asc()).all()
        return render_template('user/account_info.html',cat=cat,deets=deets)
    else:
        id = session.get('user')
        deets=db.session.query(User).filter(User.user_id==id).first()
        dob = request.form.get('dob')
        bio = request.form.get('bio')
        phone = request.form.get('phone')
        file = request.files['pix']
         #to know the filename original name
        filename= file.filename
        allowed = ['.png','.jpg','.jpeg',]
        if dob!="" and bio!="" and filename !="":
            name,ext = os.path.splitext(filename)#import os on line1
            if ext.lower() in allowed:
                name=deets.user_username
                newname = generate_name()+name+ext
                file.save("galleryapp/static/uploads/"+newname)#it will upload the picture and save it as picture.png,save it as the original filename
                #update the user using orm by keeping the name of the uploaded file for the user,then redirect to dashboard
                u = db.session.query(User).filter(User.user_id==id).first()
                # query(User).filter(User.user_id==userid).first()
                #update
                u.user_bio = bio
                u.user_pix = newname
                u.user_dob = dob
                u.user_phone=phone
                 #add to session
                db.session.commit()
        flash("<div class='alert alert-success'>Profile details Updated</div>")
        return redirect('/account')

@app.route('/studio')
def studio():
    if session.get('user') == None:
        return redirect('/login')
    else:
        id = session['user']
        deets=db.session.query(User).get(id)
        cart_items = db.session.query(Cart).filter(User.user_id==Cart.cart_userid).all()
        category= db.session.query(Category).all()
        medium=db.session.query(Medium).all()
        style=db.session.query(Style).all()
        cat = db.session.query(Category).order_by(Category.category_name.asc()).all()
        material=db.session.query(Material).all()
        subject=db.session.query(Subject).all()
        return render_template('user/studio.html',category=category,deets=deets,cart_items=cart_items,medium=medium,style=style,material=material,subject=subject,cat=cat)


@app.route('/studio/submit',methods=['POST'])
def add_artworks():
    if session.get('user') == None:
            return redirect('/login')
    else:
        id = session['user']
        deets=db.session.query(User).get(id)
        #retrieve form info
        title = request.form.get('title')
        artist = request.form.get('artist')
        categoryid = request.form.get('catid')
        medium = request.form.get('medium')
        price = request.form.get('price')
        year = request.form.get('year')
        dimension = request.form.get('dimension')
        style = request.form.get('style')
        material = request.form.get('material')
        subject = request.form.get('subject')
        #retrieve the file
        file = request.files['pix']
        #to know the filename original name
        filename= file.filename
        allowed = ['.png','.jpg','.jpeg',]
        if title!= '' and artist!= '' and categoryid!= '' and price!= '' and medium!= '' and year!= '' and dimension!= '' and filename !="" and material!= '' and subject!= '' and style!= '' :
            name,ext = os.path.splitext(filename)#import os on line1
            if ext.lower() in allowed:
                name=deets.user_username
                newname = generate_name()+name+ext
                file.save("galleryapp/static/uploads/"+newname)#it will upload the picture and save it as picture.png,save it as the original filename
                #update the user using orm by keeping the name of the uploaded file for the user,then redirect to dashboard
                userid = deets.user_id
                a = Artworks(art_title=title,art_year=year,artist_fullname=artist,art_pix=newname,art_price=price,art_dimension=dimension,upload_userid=userid,art_categoryid=categoryid,art_mediumid=medium,art_subjectid=subject,art_materialid=material,art_styleid=style)
                 #add to session
                db.session.add(a)
                db.session.commit()
                artid=Artworks.query.order_by(Artworks.art_id.desc()).first()
                art_id=artid.art_id
                ap= Product_category(product_id=art_id,category_id=categoryid,medium_id=medium,subject_id=subject,style_id=style,material_id=material)
                db.session.add(ap)
                db.session.commit()
                flash("Artwork Uploaded Succesfully")
                return redirect('/studio')
            else:
                return "File extension not allowed"
        else:
            flash("please fill in all fields")
            return redirect('/studio')

@app.route('/account/updateprod',methods=['GET','POST'])
def update_product():
    if session.get('user') == None:
        return redirect('/login')
    if request.method == 'GET':
        id = session.get('user')
        deets=db.session.query(User).filter(User.user_id==id).first()
        all_arts= db.session.query(Artworks).filter(Artworks.upload_userid==id).all()
        cat = db.session.query(Category).order_by(Category.category_name.asc()).all()
        artid = db.session.query(Artworks).filter(Artworks.art_id).all()
        category= db.session.query(Category).all()
        return render_template('user/updateprod.html',deets=deets,all_arts=all_arts,category=category,artid=artid,cat=cat)

@app.route('/account/shipping',methods=['GET','POST'])
def shipping():
    if session.get('user') == None:
        return redirect('/login')
    else:
        if request.method == 'GET':
            id = session.get('user')
            deets=db.session.query(User).filter(User.user_id==id).first()
            cat = db.session.query(Category).order_by(Category.category_name.asc()).all()
            return render_template('user/shipping.html',cat=cat,deets=deets)

# @app.route('/account/sales',methods=['GET','POST'])
# def sales():
#     if session.get('user') == None:
#         return redirect('/login')
#     else:
#         if request.method == 'GET':
#             id = session.get('user')
#             all_orders= db.session.query(Orders).all()
#             order_deets=db.session.query(Order_details).filter(Order_details.art.upload_userid==id).all()
#             deets=db.session.query(User).filter(User.user_id==id).first()
#             return render_template('user/sales.html',deets=deets,all_orders=all_orders)

@app.route('/account/orders',methods=['GET','POST'])
def orders():
    if session.get('user') == None:
        return redirect('/login')
    else:
        if request.method == 'GET':
            id = session.get('user')
            all_orders= db.session.query(Orders).filter(Orders.order_userid==id).all()
            cat = db.session.query(Category).order_by(Category.category_name.asc()).all()
            deets=db.session.query(User).filter(User.user_id==id).first()
            return render_template('user/orders.html',cat=cat,deets=deets,all_orders=all_orders)

@app.route('/account/order/<oid>/',methods=['GET','POST'])
def order_deets(oid):
    if session.get('user') == None:
        return redirect('/login')
    else:
        id = session.get('user')
        all_orders= db.session.query(Orders).filter(Orders.order_id==oid).all()
        cat = db.session.query(Category).order_by(Category.category_name.asc()).all()
        order_deet=db.session.query(Order_details).filter(Order_details.orderdetails_orderid==oid)
        art=Artworks.query.get(id)
        deets=db.session.query(User).filter(User.user_id==id).first()
        return render_template('user/order_details.html',deets=deets,all_orders=all_orders,order_deet=order_deet,art=art,cat=cat)


@app.route('/prod/<idd>/',methods=['POST','GET'])
def prod_details(idd):
    if request.method == 'GET':
        id = session.get('user')
        deets=db.session.query(User).filter(User.user_id==id).first()
        art=Artworks.query.get_or_404(idd)#
        category= db.session.query(Category).all()
        cart_items = db.session.query(Cart).filter(User.user_id==Cart.cart_userid).all()
        cat = db.session.query(Category).order_by(Category.category_name.asc()).all()
        return render_template('user/produpdate.html',deets=deets,art=art,category=category,cart_items=cart_items,cat=cat)
    else:
        #form was submitted
        title = request.form.get('title')
        artist = request.form.get('artist')
        categoryid = request.form.get('catid')
        medium = request.form.get('medium')
        year = request.form.get('year')
        dimension = request.form.get('dimension')
        #update the db using ORM method
        artobj = db.session.query(Artworks).filter(Artworks.art_id==idd).first()
        artobj.art_title = title
        artobj.art_year=year
        artobj.category_id=categoryid
        artobj.artist_fullname = artist
        db.session.commit()
        flash("<div class='alert alert-success'>Artwork details Updated</div>")
        return redirect('/account/updateprod')

@app.route('/allworks/<int:page_num>')
def browse_all(page_num):
    id = session.get('user')
    deets = db.session.query(User).get(id)
    all_fav=db.session.query(Favorites).filter(Favorites.fav_userid==id).all()
    fav = []
    for j in all_fav:
        fav.append(j.fav_artid)
    cart_items = db.session.query(Cart).filter(User.user_id==Cart.cart_userid).all()
    # all_arts= db.session.query(Artworks).order_by(func.rand()).all()
    all_arts= db.session.query(Artworks).filter(Artworks.art_status=='1').all()
    all_art= db.session.query(Artworks).filter(Artworks.art_status=='1').paginate(per_page=9, page=page_num, error_out=True)
    user = db.session.query(User).all()
    cat = db.session.query(Category).order_by(Category.category_name.asc()).all()
    med = db.session.query(Medium).order_by(Medium.medium_name.asc()).all()
    subj = db.session.query(Subject).order_by(Subject.subject_name.asc()).all()
    styl = db.session.query(Style).order_by(Style.style_name.desc()).all()
    mate = db.session.query(Material).order_by(Material.material_name.asc()).all()
    return render_template('user/allworks.html',all_arts=all_arts,deets=deets,user=user,all_fav=all_fav,cart_items=cart_items,cat=cat,med=med,subj=subj,styl=styl,mate=mate,fav=fav,all_art=all_art)

@app.route('/fil/<int:idd>',methods=['GET','POST'])
def fil(idd):
      if request.method=='GET':
          id = session.get('user')
          deets = db.session.query(User).get(id)
          all_fav=db.session.query(Favorites).all()
          cart_items = db.session.query(Cart).filter(User.user_id==Cart.cart_userid).all()
          filtered=Product_category.query.filter(Product_category.category_id==idd).all()
          items={}
          # all_arts= db.session.query(Artworks).order_by(func.rand()).all()
          all_arts= db.session.query(Artworks).filter(Artworks.art_status=='1').all()
          user = db.session.query(User).all()
          cat = db.session.query(Category).order_by(Category.category_name.asc()).all()
          med = db.session.query(Medium).order_by(Medium.medium_name.asc()).all()
          subj = db.session.query(Subject).order_by(Subject.subject_name.asc()).all()
          styl = db.session.query(Style).order_by(Style.style_name.desc()).all()
          mate = db.session.query(Material).order_by(Material.material_name.asc()).all()
          return render_template('user/allworksf.html',all_arts=all_arts,deets=deets,user=user,all_fav=all_fav,cart_items=cart_items,cat=cat,med=med,subj=subj,styl=styl,mate=mate,filtered=filtered,id=int(idd))

@app.route('/proddeets/<idd>/')
def prod_more(idd):
     if request.method == 'GET':
        id = session.get('user')
        deets=db.session.query(User).filter(User.user_id==id).first()
        art=Artworks.query.get_or_404(idd)#
        all_arts= db.session.query(Artworks).order_by(func.rand()).limit(4).all()
        cart_items = db.session.query(Cart).filter(User.user_id==Cart.cart_userid).all()
        category= db.session.query(Category).all()
        works = db.session.query(Artworks).filter(Artworks.upload_userid== idd).all()
        cat = db.session.query(Category).order_by(Category.category_name.asc()).all()
        return render_template('user/productdeets.html',works=works,art=art,category=category,deets=deets,all_arts=all_arts,cart_items=cart_items,cat=cat)

@app.route('/user/contact',methods=[ 'GET','POST'])
def contact_us():
    contact = ContactForm()
    id = session.get('user')
    deets=db.session.query(User).filter(User.user_id==id).first()
    if request.method=='GET':
        cat = db.session.query(Category).order_by(Category.category_name.asc()).all()
        return render_template('user/contactus.html',contact=contact,deets=deets,cat=cat)
    else:
        if contact.validate_on_submit():
            email = contact.email.data
            msg = contact.message.data
            c = Messages(msg_email=email,msg_content=msg)
            db.session.add(c)
            db.session.commit()
            flash('Thank you for contacting us')
            return redirect(url_for('contact_us'))
        else:
            cat = db.session.query(Category).order_by(Category.category_name.asc()).all()
            return render_template('user/contactus.html',contact=contact,deets=deets,cat=cat)

@app.route('/artist/<idd>/')
def artist(idd):
    id = session.get('user')
    works = db.session.query(Artworks).filter(Artworks.upload_userid== idd).all()
    cat = db.session.query(Category).order_by(Category.category_name.asc()).all()
    all_fav=db.session.query(Favorites).filter(Favorites.fav_userid==id).all()
    fav = []
    for j in all_fav:
        fav.append(j.fav_artid)
    all_arts= db.session.query(Artworks).filter(Artworks.upload_userid== idd).order_by(func.rand()).all()
    deets = db.session.query(User).get(id)
    for p in all_arts:
        pass
    return render_template('user/artist.html',deets=deets,works=works,all_arts=all_arts,p=p,fav=fav,cat=cat)

@app.route('/addfavorites/<id>/')
def add_favorites(id):
    if session.get('user')!= None:
        userid = session.get('user')
        artid = id
        chk=db.session.query(Favorites).filter(Favorites.fav_userid==userid).filter(Favorites.fav_artid==artid).first()
        if chk == None:
            f = Favorites(fav_userid=userid,fav_artid=artid)
            db.session.add(f)
            db.session.commit()
            flash('Item added to favorites')
            return redirect(url_for('browse_all', page_num=1))
        else:
            db.session.delete(chk)
            db.session.commit()
            flash('Item removed from favorites')
            return redirect(url_for('browse_all', page_num=1))


@app.route('/favorites/')
def favorites():
    if session.get('user') == None:
        return redirect(url_for('user_login'))
    else:
        id = session.get('user')
        deets=db.session.query(User).get(id)
        fav=db.session.query(Favorites).filter(Favorites.fav_userid==id).all()
        cat = db.session.query(Category).order_by(Category.category_name.asc()).all()
        return render_template('user/favorites.html',deets=deets,fav=fav,cat=cat)

@app.route('/cart')
def cart():
    if session.get('user') == None:
        return redirect(url_for('user_login'))
    else:
        id = session.get('user')
        total =[]
        deets=db.session.query(User).get(id)
        cat = db.session.query(Category).order_by(Category.category_name.asc()).all()
        cart_total=db.session.query(func.sum(Cart.cart_itemprice)).filter(Cart.cart_userid==id).first()
        cart_items=db.session.query(Cart).filter(Cart.cart_userid==id).all()
        all_arts= db.session.query(Artworks).order_by(func.rand()).all()
        return render_template('user/cart.html',deets=deets,all_arts=all_arts,cart_items=cart_items,total=total,cart_total=cart_total,cat=cat)

#add to cart
@app.route('/cart/<add>/')
def add_cart(add):
    if session.get('user') == None:
        return redirect(url_for('user_login'))
    else:
        citm=[]
        id = session.get('user')
        deets=db.session.query(User).get(id)
        price_obj=db.session.query(Artworks).filter(Artworks.art_id==add).first()
        price=price_obj.art_price
        cartitemid= db.session.query(Cart).filter(Cart.cart_artid==add).all()
        for c in cartitemid:
            citm.append(c.cart_artid)
        if int(add) in citm:
            flash('item already in cart')
            return redirect('/allworks/1')
        else:
            c = Cart(cart_artid=add,cart_userid=id,cart_itemprice=price)
            db.session.add(c)
            db.session.commit()
            return redirect('/cart')

#delete cart item
@app.route('/del/<dl>/')
def del_cart(dl):
    if session.get('user') == None:
        return redirect(url_for('user_login'))
    else:
        id = session.get('user')
        c = Cart.query.get_or_404(dl)
        db.session.delete(c)
        db.session.commit()
        return redirect('/cart')

@app.route('/checkout',methods=['GET','POST'])
def checkout():
    if session.get('user') == None:
        return redirect(url_for('user_login'))
    else:
        if request.method == 'GET':
            id = session.get('user')
            cart_total=db.session.query(func.sum(Cart.cart_itemprice)).filter(Cart.cart_userid==id).first()
            cart_item=db.session.query(Cart).filter(Cart.cart_userid==id).all()
            deets=db.session.query(User).get(id)
            a=deets.user_address
            cat = db.session.query(Category).order_by(Category.category_name.asc()).all()
            return render_template('user/checkout.html',deets=deets,cart_item=cart_item,cart_total=cart_total,a=a,cat=cat)
        else:
            pass

@app.route('/payment',methods=['GET','POST'])
def make_payment():
    if session.get('user') == None:
        return redirect(url_for('user_login'))
    else:
        if request.method == 'GET':
            id = session.get('user')
            cart_total=db.session.query(func.sum(Cart.cart_itemprice)).filter(Cart.cart_userid==id).first()
            cart_item=db.session.query(Cart).filter(Cart.cart_userid==id).all()
            deets=db.session.query(User).get(id)
            cat = db.session.query(Category).order_by(Category.category_name.asc()).all()
            return render_template('user/checkout.html',deets=deets,cart_item=cart_item,cart_total=cart_total,cat=cat)
        else:
            #
            id = session.get('user')
            user=User.query.get(id)
            cart_item=db.session.query(Cart).filter(Cart.cart_userid==id).all()
            cart_total=db.session.query(func.sum(Cart.cart_itemprice)).filter(Cart.cart_userid==id).first()
            o = Orders(order_amt=cart_total[0],order_userid=id,order_address=user.user_address,order_phone=user.user_phone)
            db.session.add(o)
            db.session.commit()
            session['order_id']=o.order_id
            refno = int(random.random() * 120030)
            session['reference']=refno
            #get last Order
            last_order = Orders.query.order_by(Orders.order_id.desc()).first()
            #populating items from cart into order details table
            for i in cart_item:
                od = Order_details(
                    orderdetails_orderid=last_order.order_id,
                    orderdetails_amt=last_order.order_amt,
                    orderdetails_artid=i.cart_artid
                    )
                db.session.add(od)
                db.session.commit()
                db.session.delete(i)
                db.session.commit()

            return redirect('confirm')


@app.route('/confirm',methods=['GET','POST'])
def confirm():
    if request.method=='GET':
        id = session.get('user')
        user=User.query.get(id)
        cat = db.session.query(Category).order_by(Category.category_name.asc()).all()
        order=Orders.query.get(session['order_id'])
        order_deets=db.session.query(Order_details).filter(Order_details.orderdetails_orderid==session['order_id']).all()
        user_email=user.user_email
        pay_amt=order.order_amt
        return render_template('user/confirmpayment.html',user=user,email=user_email,amt=pay_amt,refno=session['reference'],cat=cat)
    else:
        #update payment table
        p = Payment(payment_orderid=session['order_id'],payment_refno=session['reference'],payment_userid=session['user'])
        db.session.add(p)
        db.session.commit()

        #get order id
        order=Orders.query.get(session['order_id'])
        id = session.get('user')
        user=User.query.get(id)
        user_email=user.user_email
        pay_amt=order.order_amt
        headers={"Content-Type":"application/json",
                 "Authorization":"Bearer sk_test_d151a6d37c626f9ba7589678d5a58a3933101099"}
        data ={"amount":pay_amt,
               "reference":session['reference'],
               "order_id":session['order_id'],
               "email":user_email}
        response = requests.post('https://api.paystack.co/transaction/initialize',
                                headers=headers,data=json.dumps(data))
        rspjson = json.loads(response.text)
        if rspjson['status'] == True:
            url = rspjson['data']['authorization_url']
            return redirect(url)
        else:
            return redirect('/confirm')

@app.route('/update/address', methods=['GET','POST'])
def address():
     if request.method=='GET':
        id = session.get('user')
        cart_item=db.session.query(Cart).filter(Cart.cart_userid==id).all()
        cart_total=db.session.query(func.sum(Cart.cart_itemprice)).filter(Cart.cart_userid==id).first()
        num =request.args.get('number')
        street =request.args.get('street')
        city =request.args.get('city')
        phone =request.args.get('phone')
        address=num+', '+street+', '+city

        #populate user address
        deets=db.session.query(User).get(id)
        deets.user_address=address
        db.session.commit()
        #populating order table with cart info
        o = Orders(order_amt=cart_total[0],order_userid=id,order_address=address,order_phone=phone)
        db.session.add(o)
        db.session.commit()
        last_order = Orders.query.order_by(Orders.order_id).filter(Orders.order_userid==id).first()
        order=db.session.query(Orders)

        #store orderid and refno in session
        session['order_id']=o.order_id
        refno = int(random.random() * 120030)
        session['reference']=refno
        return "Done"

@app.route('/paystack')
def paystack():
    refid = session.get('reference')
    if refid == None:
        return redirect('/')
    else:
        id = session.get('user')
        deets=db.session.query(User).get(id)
        #connect to paystack verify
        headers={"Content-Type": "application/json", "Authorization":"Bearer sk_test_d151a6d37c626f9ba7589678d5a58a3933101099"}
        verifyurl = "https://api.paystack.co/transaction/verify/"+str(refid)
        response=requests.get(verifyurl,headers=headers)
        rspjson=json.loads(response.text)
        if rspjson['status']==True:
             #update Order table
            o=db.session.query(Orders).filter(Orders.order_userid==id).order_by(Orders.order_id.desc()).first()
            o.order_status='success'
            db.session.commit()
            #update payment table
            p=db.session.query(Payment).filter(Payment.payment_userid==id).order_by(Payment.payment_orderid.desc()).first()
            p.payment_amt=rspjson['data']['amount']
            p.payment_status=rspjson['data']['status']
            db.session.commit()
            #update Artwork availability status table
            od=db.session.query(Order_details).filter(Order_details.orderdetails_orderid==o.order_id).all()
            for j in od:
                art_av = db.session.query(Artworks).filter(j.orderdetails_artid==Artworks.art_id).one()
                art_av.art_availablestatus='0'
                db.session.commit()
            # session.pop('reference')
            # session.pop('order_id')
            #paument was successful
            cat = db.session.query(Category).order_by(Category.category_name.asc()).all()
            return render_template('user/paystack.html',rspjson=rspjson,deets=deets,refid=refid,cat=cat)
        else:
            p=db.session.query(Payment).filter(Payment.payment_userid==id).order_by(Payment.payment_orderid.desc()).first()
            p.payment_amt=rspjson['amount']
            p.payment_status=rspjson['data']['status']
            db.session.commit()
            #payment failed
            return render_template('user/paystackf.html',rspjson=rspjson)

@app.route('/subscribe/newsletter',methods=['GET','POST'])
def newsletter():
    if request.method=='POST':
        pass
    else:
        subcscribed=db.session.query(Newsletter.email).all()
        mail_list=[]
        for i in subcscribed:
            mail_list.append(i[0])
        #get email address from ajax
        mail = request.args.get('email')
        if is_valid_email(mail):
            if mail in mail_list:
                return "Already Registered"
            else:
                if str(mail) not in mail_list and mail != '':
                    n = Newsletter(email=mail)
                    db.session.add(n)
                    db.session.commit()
                    return "Subscribed successfully"
                else:
                    return 'Enter an Email address'
        else:
            return 'enter a valid Email address'

@app.route('/category/<idd>',methods=['GET','POST'])
def cat_filter(idd):
    if request.method=='GET':
        idds=([])
        filtered=Product_category.query.filter(Product_category.category_id==idd).all()
        for i in filtered:
            idds.append(i.product_id)
        return jsonify(idds)

@app.route('/blog', methods=['GET','POST'])
def blog():
    return render_template('user/blog.html')


@app.route('/temp')
def template():
        id = session.get('user')
        works = db.session.query(Artworks).order_by(func.rand()).first()
        deets=db.session.query(User).get(id)
        cart_items=db.session.query(Cart).filter(Cart.cart_userid==id).all()
        cat = db.session.query(Category).order_by(Category.category_name.asc()).all()
        cart_total=db.session.query(func.sum(Cart.cart_itemprice)).filter(Cart.cart_userid==id).first()
        username=User.user_username
        return render_template('user/template.html',username=username,deets=deets,works=works,cart_items=cart_items,cart_total=cart_total,cat=cat)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('user/error404.html',error=error),404

@app.errorhandler(500)
def internal_error(error):
    return "Sorry an error occoured, please try again later",500
