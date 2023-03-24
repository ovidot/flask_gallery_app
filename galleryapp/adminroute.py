#import 3rd party
import os,random,string
from flask import render_template,request,redirect,flash,session,url_for
from sqlalchemy import or_
#import from local files
from werkzeug.security import generate_password_hash,check_password_hash
from galleryapp import app,db
from galleryapp.models import User,Admin,Category,Artworks,Medium,Style,Material,Subject,Orders,Order_details


# ADMIN START

@app.route('/admin',methods=['GET','POST'])
def admin():
    if request.method == 'GET':
        if session.get('admin') ==None:
            flash('login to access Admin Dashboard')
            return redirect('/admin/login')
        else:
            return render_template('admin/index.html')
    else:
        return render_template('admin/index.html')


@app.route('/admin/login',methods=['POST','GET'])
def adminlogin():
    if request.method == 'GET':
        return render_template('admin/adminlogin.html')
    else:
        #retrieve form data
        username=request.form.get('uname')
        pwd = request.form.get('pwd')
        #check for username in database
        deets = db.session.query(Admin).filter(Admin.admin_username==username).first()
        if deets != None:
            pwdindb = deets.admin_password
            if pwdindb == pwd:
                id = deets.admin_id
                session['admin']=id
                return redirect('/admin')
            else:
                flash('invalid credentials')
                return redirect('/admin/login')
        else:
            flash('invalid credentials')
            return redirect('/admin/login')

@app.route('/admin/logout')
def admin_logout():
    if session.get('admin') !=None:
        session.pop('admin',None)
    return redirect('/admin/login')


@app.route('/admin/category',methods=['GET','POST'])
def admin_category():
    if session.get('admin') ==None:
        return redirect('/admin/login')
    else:
        if request.method == 'GET':
            cat = db.session.query(Category).order_by(Category.category_name.asc()).all()
            med = db.session.query(Medium).order_by(Medium.medium_name.asc()).all()
            subj = db.session.query(Subject).order_by(Subject.subject_name.asc()).all()
            styl = db.session.query(Style).order_by(Style.style_name.desc()).all()
            mate = db.session.query(Material).order_by(Material.material_name.asc()).all()
            return render_template('admin/category.html',cat=cat,med=med,subj=subj,styl=styl,mate=mate)
        else:
            data=request.form
            cat_name= data.get('catname')
            medium= data.get('medium')
            style=data.get('style')
            subject=data.get('subject')
            material=data.get('material')
            if cat_name!='':
                c = Category(category_name = cat_name)
                db.session.add(c)
            else:
                pass
            if medium!='':
                m= Medium(medium_name=medium)
                db.session.add(m)
            else:
                pass
            if style!='':
                st=Style(style_name=style)
                db.session.add(st)
            else:
                pass
            if material!='':
                mat=Material(material_name=material)
                db.session.add(mat)
            else:
                pass
            if subject!='':
                sub=Subject(subject_name=subject)
                db.session.add(sub)
            else:
                pass
            db.session.commit()
            flash(' add successfully')
            return redirect('/admin/category')

@app.route('/admin/users')
def manage_users():
    if session.get('admin') ==None:
        return redirect('/admin/login')
    else:
        users = db.session.query(User).order_by(User.user_fname.desc()).all()
        return render_template('/admin/users.html',users=users)

@app.route('/admin/products')
def manage_arts():
    if session.get('admin') == None:
        return redirect('/admin/login')
    else:
        id = session['admin']
        all_arts= db.session.query(Artworks).order_by(Artworks.upload_date.desc()).all()
        return render_template('/admin/products.html',all_arts=all_arts)

@app.route('/admin/products/<idd>')
def manage_artinfo(idd):
    if session.get('admin') == None:
        return redirect('/admin/login')
    else:
        id = session['admin']
        art= db.session.query(Artworks).filter(Artworks.art_id==idd).first()
        cat = Category.query.join(Artworks).filter(Category.category_id==Artworks.art_categoryid).first()
        med = Medium.query.join(Artworks).filter(Medium.medium_id==Artworks.art_mediumid).first()
        subj = Subject.query.join(Artworks).filter(Subject.subject_id==Artworks.art_subjectid).first()
        styl = Style.query.join(Artworks).filter(Style.style_id==Artworks.art_styleid).first()
        mate = Material.query.join(Artworks).filter(Material.material_id==Artworks.art_materialid).first()
      #  flash('status updated')
        return render_template('/admin/productedit.html',art=art,cat=cat,med=med,subj=subj,styl=styl,mate=mate)

@app.route('/admin/update_artstatus',methods=['POST'])
def update_topic():
    if session.get('admin') !=None:
        newstatus = request.form.get('status')
        artid=request.form.get('art-id')
        st=db.session.query(Artworks).get(artid)
        st.art_status=newstatus
        db.session.commit()
        flash("Artwork successfully updated!!!")
        return redirect(url_for('manage_arts'))
    else:
        return redirect('/admin/login')

@app.route('/admin/orders')
def manage_orders():
    if session.get('admin') == None:
        return redirect('/admin/login')
    else:
        id = session['admin']
        all_orders= db.session.query(Orders).all()
        return render_template('/admin/orders.html',all_orders=all_orders)

@app.route('/admin/orders/<oid>/',methods=['GET','POST'])
def order_dts(oid):
    if session.get('admin') == None:
        return redirect('/admin/login')
    else:
        all_orders= db.session.query(Orders).filter(Orders.order_id==oid).all()
        order_deet=db.session.query(Order_details).filter(Order_details.orderdetails_orderid==oid)
        users = db.session.query(User).order_by(User.user_fname.desc()).all()
        return render_template('admin/order_details.html',all_orders=all_orders,order_deet=order_deet)

@app.route('/admin/category/<dell>/')
def delete_cat(dell):
    if session.get('admin') == None:
        return redirect('/admin/login')
    else:
        cat=db.session.query(Category).filter(Category.category_id==dell).first()
        db.session.delete(cat)
        db.session.commit()
    return redirect('/admin/category')

@app.route('/admin/medium/<dell>/')
def delete_med(dell):
    if session.get('admin') == None:
        return redirect('/admin/login')
    else:
        med=db.session.query(Medium).filter(Medium.medium_id==dell).first()
        db.session.delete(med)
        db.session.commit()
    return redirect('/admin/category')

@app.route('/admin/style/<dell>/')
def delete_style(dell):
    if session.get('admin') == None:
        return redirect('/admin/login')
    else:
        sty=db.session.query(Style).filter(Style.style_id==dell).first()
        db.session.delete(sty)
        db.session.commit()
    return redirect('/admin/category')

@app.route('/admin/material/<dell>/')
def delete_material(dell):
    if session.get('admin') == None:
        return redirect('/admin/login')
    else:
        sty=db.session.query(Material).filter(Material.material_id==dell).first()
        db.session.delete(sty)
        db.session.commit()
    return redirect('/admin/category')

@app.route('/admin/subject/<dell>/')
def delete_subject(dell):
    if session.get('admin') == None:
        return redirect('/admin/login')
    else:
        subj=db.session.query(Subject).filter(Subject.subject_id==dell).first()
        db.session.delete(subj)
        db.session.commit()
    return redirect('/admin/category')

#ADMIN END



# @app.route('/loginsubmit',methods=['POST'])
# def form_submit():
#     data=request.form
#     uname=data.get('username')
#     pwd=data.get('password')
#     return render_template('admin/login',uname,pwd)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('error404.html',error=error),404

@app.errorhandler(500)
def internal_error(error):
    return "Sorry an error occoured, please try again later",500

