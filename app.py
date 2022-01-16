from datetime import date
from flask import Flask,render_template,request,url_for, redirect,flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from flask_login import UserMixin,LoginManager,login_user,login_required,logout_user,current_user
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///asteri_platina.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(app)
login_manager=LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(userid):
    k=users.query.all() 
    if len(k)!=0:   
        user=users.query.filter_by(id=userid).first()
        return users.query.get(user.id)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return render_template("index.html",id=None)
# table creation

class UserEmail(db.Model):
    email_id=db.Column(db.String(50),primary_key=True)
    password=db.Column(db.String(200),nullable=False)

class UserIdentity(db.Model):
    UniqueID =db.Column(db.String(50),primary_key=True)
    user_name=db.Column(db.String(200),unique=True,nullable=False)
    mobile=db.Column(db.Integer,unique=True,nullable=False)

class users(db.Model,UserMixin):
    id =db.Column(db.String(10),primary_key=True)
    email_id=db.Column(db.String(50),db.ForeignKey(UserEmail.email_id),nullable=False)
    UniqueID=db.Column(db.String(50),db.ForeignKey(UserIdentity.UniqueID),unique=True,nullable=False)

class UserAddress(db.Model):
    id =db.Column(db.String(10),db.ForeignKey(users.id),primary_key=True)
    DoorNo=db.Column(db.String(10),nullable=False)
    Street=db.Column(db.String(100),nullable=False)
    Area=db.Column(db.String(100),nullable=False)
    City=db.Column(db.String(50),nullable=False)
    State=db.Column(db.String(50),nullable=False)
    Pincode=db.Column(db.String(6),nullable=False)

class Admins(db.Model):
    admin_id=db.Column(db.String(10),db.ForeignKey(users.id),primary_key=True)
    admin_desig=db.Column(db.String(30),nullable=False)

class NGO(db.Model):
    NGO_id=db.Column(db.String(10),db.ForeignKey(users.id),primary_key=True)

class Donor(db.Model):
    donor_id=db.Column(db.String(10),db.ForeignKey(users.id),primary_key=True)
    dob=db.Column(db.String(15),nullable=False)
 
   
class Requestor(db.Model):
    requestor_id=db.Column(db.String(10),db.ForeignKey(users.id),primary_key=True)
    dob=db.Column(db.String(15),nullable=False)

class BlockedUsers(db.Model):
    donor_id=db.Column(db.String(10),db.ForeignKey(Donor.donor_id),primary_key=True)
    block_reason=db.Column(db.String(20),nullable=False)
    block_date=db.Column(db.String(15),nullable=False)
    admin_id=db.Column(db.Integer,db.ForeignKey(Admins.admin_id),nullable=False)

class Medicine(db.Model):
    med_id=db.Column(db.Integer,primary_key=True)
    med_name=db.Column(db.String,unique=True,nullable=False)

class MedicineEffects(db.Model):
    med_id=db.Column(db.Integer,db.ForeignKey(Medicine.med_id),nullable=False,primary_key=True)
    med_effects=db.Column(db.String(50),nullable=False,primary_key=True)

class MedicineClass(db.Model):
    med_id=db.Column(db.Integer,db.ForeignKey(Medicine.med_id),nullable=False,primary_key=True)
    med_class=db.Column(db.String(50),nullable=False,primary_key=True)

class RequestedMedicine(db.Model):
    request_id=db.Column(db.Integer,primary_key=True)
    med_id=db.Column(db.Integer,db.ForeignKey(Medicine.med_id),nullable=False)
    need_date=db.Column(db.String(15),nullable=False)
    requested_date=db.Column(db.String(15),nullable=False)
    requested_quantity=db.Column(db.Integer,nullable=False)
    requestor_id=db.Column(db.Integer,db.ForeignKey(Requestor.requestor_id),nullable=False)

class DonatedMedicine(db.Model):
    donation_id=db.Column(db.Integer,primary_key=True)
    med_id=db.Column(db.Integer,db.ForeignKey(Medicine.med_id),nullable=False)
    donation_expiry=db.Column(db.String(15),nullable=False)
    donation_quantity=db.Column(db.Integer,nullable=False)
    donor_id=db.Column(db.Integer,db.ForeignKey(Donor.donor_id),nullable=False)

class DeliveredMedicine(db.Model):
    delivery_id=db.Column(db.Integer,primary_key=True)
    request_id=db.Column(db.Integer,db.ForeignKey(RequestedMedicine.request_id),unique=True,nullable=False)
    delivery_date=db.Column(db.String(15),nullable=False)
    delivered_quantity=db.Column(db.Integer,nullable=False)
    donation_id=db.Column(db.Integer,db.ForeignKey(DonatedMedicine.donation_id),unique=True,nullable=False)

class Announcement(db.Model):
    request_id=db.Column(db.Integer,db.ForeignKey(RequestedMedicine.request_id),primary_key=True)


# Table creation completed


@app.route("/")
def hello_world():
    return render_template("index.html",id=current_user.get_id())



@app.route("/login")
def login():
    return render_template("login.html",id=current_user.get_id())

@app.route("/requestor_login", methods=['GET', 'POST'])
def requestor_login():
    logout_user()
    if request.method=="POST":
        username=request.form['id']
        password=request.form['password']
        requestor= Requestor.query.filter_by(requestor_id=username).first()
        if(requestor is not None):
            user=users.query.filter_by(id=username).first()
            useremail=UserEmail.query.filter_by(email_id=user.email_id).first()
            if useremail.password==password:
                login_user(user)
                return redirect(url_for('requestor_homepage'))
    return render_template("requestor_login.html")

@app.route("/donor_login", methods=['GET', 'POST'])
def donor_login():
    logout_user()
    if request.method=="POST":
        username=request.form['id']
        password=request.form['password']
        donor= Donor.query.filter_by(donor_id=username).first()
        if(donor is not None):
            user=users.query.filter_by(id=username).first()
            useremail=UserEmail.query.filter_by(email_id=user.email_id).first()
            if useremail.password==password:
                login_user(user)
                return redirect(url_for('donor_homepage'))
    return render_template("donor_login.html")

@app.route("https://asteri-platina.herokuapp.com/admin_login/admin_login", methods=['GET', 'POST'])
def admin_login():
    logout_user()
    if request.method=="POST":
        username=request.form['id']
        password=request.form['password']
        admin= Admins.query.filter_by(admin_id=username).first()
        if(admin is not None):
            user=users.query.filter_by(id=username).first()
            useremail=UserEmail.query.filter_by(email_id=user.email_id).first()
            if useremail.password==password:
                login_user(user)
                return redirect(url_for('admin_homepage'))
    return render_template("admin_login.html")

@app.route("/ngo_login", methods=['GET', 'POST'])
def ngo_login():
    logout_user()
    if request.method=="POST":
        username=request.form['id']
        password=request.form['password']
        ngo= NGO.query.filter_by(NGO_id=username).first()
        if(ngo is not None):
            user=users.query.filter_by(id=username).first()
            useremail=UserEmail.query.filter_by(email_id=user.email_id).first()
            if useremail.password==password:
                login_user(user)
                return redirect(url_for('ngo_homepage'))
    return render_template("ngo_login.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/donor_signup", methods=['GET', 'POST'])
def donor_signup():
    if request.method=="POST":
        try:
            email=request.form['email']
            username=request.form['username']
            password=request.form['password']
            mobile=request.form['mobile']
            dob=request.form['dob']
            unique_id=request.form['unique_id']
            door_no=request.form['door_no']
            street=request.form['street']
            area=request.form['area']
            city=request.form['city']
            state=request.form['state']
            pincode=request.form['pincode']
            useremail=UserEmail(email_id=email,password=password)
            db.session.add(useremail)
            useridentity=UserIdentity(UniqueID=unique_id,user_name=username,mobile=mobile)
            db.session.add(useridentity)
            q=Donor.query.all()
            id="DON"+str(len(q)+1)
            print("for testing id = ",id)
            user=users(id=id,email_id=email,UniqueID=unique_id)
            db.session.add(user)
            useraddress=UserAddress(id=id,DoorNo=door_no,Street=street,Area=area,City=city,State=state,Pincode=pincode)
            db.session.add(useraddress)
            donor=Donor(donor_id=id,dob=str(dob))
            db.session.add(donor)
            db.session.commit()
            return render_template("donor_signup.html",id=id)
        except:
            db.session.rollback()
            flash("Given details already exists")
            return render_template("requestor_signup.html",id="")
        
    return render_template("donor_signup.html",id="")

@app.route("/requestor_signup", methods=['GET', 'POST'])
def requestor_signup():
    if request.method=="POST":
        try:
            email=request.form['email']
            username=request.form['username']
            password=request.form['password']
            mobile=request.form['mobile']
            dob=request.form['dob']
            unique_id=request.form['unique_id']
            door_no=request.form['door_no']
            street=request.form['street']
            area=request.form['area']
            city=request.form['city']
            state=request.form['state']
            pincode=request.form['pincode']
            useremail=UserEmail(email_id=email,password=password)
            db.session.add(useremail)
            useridentity=UserIdentity(UniqueID=unique_id,user_name=username,mobile=mobile)
            db.session.add(useridentity)
            q=Requestor.query.all()
            id="REQ"+str(len(q)+1)
            print("for testing id = ",id)
            user=users(id=id,email_id=email,UniqueID=unique_id)
            db.session.add(user)
            useraddress=UserAddress(id=id,DoorNo=door_no,Street=street,Area=area,City=city,State=state,Pincode=pincode)
            db.session.add(useraddress)
            requestor=Requestor(requestor_id=id,dob=str(dob))
            db.session.add(requestor)
            db.session.commit()
            return render_template("requestor_signup.html",id=id)
        except:
            db.session.rollback()
            flash("Given details already exists")
            return render_template("requestor_signup.html",id="")
    return render_template("requestor_signup.html",id="")

@app.route("/ngo_signup", methods=['GET', 'POST'])
def ngo_signup():
    if request.method=="POST":
        try:
            email=request.form['email']
            username=request.form['username']
            password=request.form['password']
            mobile=request.form['mobile']
            unique_id=request.form['unique_id']
            door_no=request.form['door_no']
            street=request.form['street']
            area=request.form['area']
            city=request.form['city']
            state=request.form['state']
            pincode=request.form['pincode']
            useremail=UserEmail(email_id=email,password=password)
            db.session.add(useremail)
            useridentity=UserIdentity(UniqueID=unique_id,user_name=username,mobile=mobile)
            db.session.add(useridentity)
            q=NGO.query.all()
            id="NGO"+str(len(q)+1)
            print("for testing id = ",id)
            user=users(id=id,email_id=email,UniqueID=unique_id)
            db.session.add(user)
            useraddress=UserAddress(id=id,DoorNo=door_no,Street=street,Area=area,City=city,State=state,Pincode=pincode)
            db.session.add(useraddress)
            ngo=NGO(NGO_id=id)
            db.session.add(ngo)
            db.session.commit()
            return render_template("ngo_signup.html",id=id)
        except:
            db.session.rollback()
            flash("Given details already exists")
            return render_template("requestor_signup.html",id="")
        
    return render_template("ngo_signup.html",id="")

@app.route("/user_profile")
@login_required
def userprofile():
    return render_template("user_profile.html",id=current_user.get_id())

@app.route("/donor_homepage", methods=['GET', 'POST'])
@login_required
def donor_homepage():
    id=str(current_user.get_id())
    if id[:3]=="DON":
        med=Medicine.query.all()  
        if request.method=="POST":
            d=BlockedUsers.query.filter_by(donor_id=id).first()
            try:
                if d.donor_id==id:
                    flash("You are blocked")
            except:
                medicine=request.form['medicine']
                quantity=request.form['quantity']
                expirydate=request.form['expirydate']
                q=DonatedMedicine.query.all()
                donation_id=len(q)+1
                donmed=DonatedMedicine(donation_id=donation_id,med_id=medicine,donation_expiry=expirydate,donation_quantity=quantity,donor_id=current_user.get_id())
                db.session.add(donmed)
                db.session.commit()
        prev_donations=DonatedMedicine.query.filter_by(donor_id=id) 
        donor_details=users.query.filter_by(id=id)  
        user_identity=UserIdentity.query.filter_by(UniqueID=donor_details[0].UniqueID)
        em=Announcement.query.all() 
        l=list()
        for i in em:
            t=RequestedMedicine.query.filter_by(request_id=i.request_id).first()
            if t is not None:
                id=t.med_id
                n=Medicine.query.filter_by(med_id=id)
                l.append(n[0].med_name)
        return render_template("donor_homepage.html",id=current_user.get_id(),med_list=med,prev_donations=prev_donations,donor_details=donor_details,user_identity=user_identity,l=l)
        
    else:
        return render_template("forbidden.html")

@app.route("/requestor_homepage", methods=['GET', 'POST'])
@login_required
def requestor_homepage():
    id=str(current_user.get_id())
    if id[:3]=="REQ":
        med=Medicine.query.all()
        if request.method=="POST":
            medicine=request.form['medicine']
            quantity=request.form['quantity']
            lastdate=request.form['lastdate']
            q=RequestedMedicine.query.all()
            request_id=len(q)+1
            reqmed=RequestedMedicine(request_id=request_id,med_id=medicine,need_date=lastdate,requested_date=str(date.today()),requested_quantity=quantity,requestor_id=current_user.get_id())
            db.session.add(reqmed)
            db.session.commit()
        prev_requests=RequestedMedicine.query.filter_by(requestor_id=id)    
        requestor_details=users.query.filter_by(id=id)  
        user_identity=UserIdentity.query.filter_by(UniqueID=requestor_details[0].UniqueID)   
        context={
            'id':current_user.get_id(),
            'med_list':med,
            'prev_requests':prev_requests,
            'requestor_details':requestor_details,
            'user_identity':user_identity
        }
        return render_template("requestor_homepage.html",**context)
    else:
        return render_template("forbidden.html")


@app.route("/ngo_homepage", methods=['GET', 'POST'])
@login_required
def ngo_homepage():
    id=str(current_user.get_id())
    if id[:3]=="NGO":
        med=Medicine.query.all()
        if request.method=="POST" and request.form['dist']==str(100):
            medicine=request.form['r_medicine']
            quantity=request.form['r_quantity']
            lastdate=request.form['r_lastdate']
            q=RequestedMedicine.query.all()
            request_id=len(q)+1
            reqmed=RequestedMedicine(request_id=request_id,med_id=medicine,need_date=lastdate,requested_date=str(date.today()),requested_quantity=quantity,requestor_id=current_user.get_id())
            db.session.add(reqmed)
            db.session.commit()
        elif request.method=="POST" and request.form['dist']==str(102):
            medicine=request.form['d_medicine']
            quantity=request.form['d_quantity']
            expirydate=request.form['d_expirydate']
            q=DonatedMedicine.query.all()
            donation_id=len(q)+1
            donmed=DonatedMedicine(donation_id=donation_id,med_id=medicine,donation_expiry=expirydate,donation_quantity=quantity,donor_id=current_user.get_id())
            db.session.add(donmed)
            db.session.commit()

        prev_requests=RequestedMedicine.query.filter_by(requestor_id=id)    
        prev_donations=DonatedMedicine.query.filter_by(donor_id=id) 
        ngo_details=users.query.filter_by(id=id)  
        user_identity=UserIdentity.query.filter_by(UniqueID=ngo_details[0].UniqueID)
        context={
            'id':current_user.get_id(),
            'med_list':med,
            'prev_requests':prev_requests,
            'prev_donations':prev_donations,
            'ngo_details':ngo_details,
            'user_identity':user_identity
        } 
        return render_template("ngo_homepage.html",**context)
    else:
        return render_template("forbidden.html")

@app.route("/admin_homepage", methods=['GET', 'POST'])
@login_required
def admin_homepage():
    id=str(current_user.get_id())
    if id[:3]=="ADM":
        if request.method=="POST":
            #uncomment below lines to add accept and reject
            # if request.form['identifier']=="form1":
            #     request_id=request.form['request_id']
            #     if request.form['submit_button']=="accept":
            #         f=str(str(request_id)+" request "+"accepted")
            #         flash(f)
            #     elif request.form['submit_button']=="reject":
            #         f=str(str(request_id)+" request "+"rejected")
            #         flash(f)
            # elif request.form['identifier']=="form2":
            #     donation_id=request.form['donation_id']
            #     if request.form['submit_button']=="accept":
            #         f=str(str(donation_id)+" donation "+"accepted")
            #         flash(f)
            #     elif request.form['submit_button']=="reject":
            #         f=str(str(donation_id)+" donation "+"rejected")
            #         flash(f)
            if request.form['identifier']=="block_form":
                try:
                    donor_id=request.form['user']
                    try:
                        if Donor.query.filter_by(donor_id=donor_id)[0] is not None:
                            block_reason=request.form['reason']
                            block_date=str(date.today())
                            admin_id=current_user.get_id()
                            block=BlockedUsers(donor_id=donor_id,block_reason=block_reason,block_date=block_date,admin_id=admin_id)
                            db.session.add(block)
                            db.session.commit()
                            f="Donor "+str(donor_id)+" blocked"
                            flash(f)
                    except:
                        # To clear blocked users table uncomment below line
                        # s=BlockedUsers.query.all()
                        # for i in s:
                        #     db.session.delete(i)
                        # db.session.commit()
                        db.session.rollback()
                        flash("The donor does not exist")
                    
                except IntegrityError:
                    db.session.rollback()
                    flash("The user is already blocked")
                
            elif request.form['identifier']=="unblock_form":
                try:
                    donor_id=request.form['user']
                    user=BlockedUsers.query.filter_by(donor_id=donor_id).first()
                    db.session.delete(user)
                    db.session.commit()
                    f="Donor "+str(donor_id)+" unblocked"
                    flash(f)
                except:
                    db.session.rollback()
                    flash("The user is already unblocked")

            elif request.form['identifier']=="add_medicine":
                try:
                    med_name=request.form["med_name"]
                    med_effects=request.form["med_effects_list"]
                    l=med_effects.split(",")
                    med_class=request.form["med_class"]
                    j=med_class.split(",")
                    med_id=str(len(Medicine.query.all())+1)                      
                    med=Medicine(med_id=med_id,med_name=med_name)
                    db.session.add(med)
                    for i in l:
                        effects=MedicineEffects(med_id=med_id,med_effects=i)
                        db.session.add(effects)
                    for i in j:
                        medclass=MedicineClass(med_id=med_id,med_class=i)
                        db.session.add(medclass)
                    db.session.commit()
                except:
                    db.session.rollback()
                    flash("Medicine already exist")
            elif request.form['identifier']=="deliver":
                try:
                    request_id=request.form["request_id"]
                    delivery_date=request.form["delivery_date"]
                    delivered_quantity=request.form["delivered_quantity"]
                    donation_id=request.form["donation_id"]
                    t=DeliveredMedicine.query.all()
                    delivery_id=len(t)+1
                    deliv=DeliveredMedicine(delivery_id=delivery_id,request_id=request_id,delivery_date=str(delivery_date),delivered_quantity=delivered_quantity,donation_id=donation_id)
                    db.session.add(deliv)
                    db.session.commit()
                except IntegrityError:
                    db.session.rollback()
                    flash("Delivery already done")
                except:
                    db.session.rollback()
                    flash("Details entered are wrong")
            elif request.form['identifier']=="emergency":
                try:
                    request_id=request.form["request_id"]
                    em=Announcement(request_id=request_id)
                    db.session.add(em)
                    db.session.commit()
                except:
                    db.session.rollback()
                    flash("Details already entered")

                    
        req_list=RequestedMedicine.query.all()
        don_list=DonatedMedicine.query.all()
        donor_list=Donor.query.all()
        blocked_list=BlockedUsers.query.all()
        count_donor=len(donor_list)
        count_requestor=len(Requestor.query.all())
        count_blocked=len(blocked_list)
        count_ngo=len(NGO.query.all())
        del_list=DeliveredMedicine.query.all()    
        admin_details=users.query.filter_by(id=id)  
        l=list()
        for i in del_list:
            l.append(i.request_id)
        context={
            'id':current_user.get_id(),
            'req_list':req_list,
            'don_list':don_list,
            'donor_list':donor_list,
            'blocked_list':blocked_list,
            'admin_details':admin_details,
            'count_donor':count_donor,
            'count_requestor':count_requestor,
            'count_ngo':count_ngo,
            'count_blocked':count_blocked,
            'available_med':len(don_list)-len(del_list),
            'l':l
        }
        return render_template("admin_homepage.html",**context)
    else:
        return render_template("forbidden.html")





def medinit():
    k=Medicine.query.all() 
    if len(k)==0:
        med=Medicine(med_id="01",med_name="Amoxicillin")
        db.session.add(med)
        med=Medicine(med_id="02",med_name="Ampicillin")
        db.session.add(med)
        med=Medicine(med_id="03",med_name="Advair")
        db.session.add(med)
        med=Medicine(med_id="04",med_name="Singulair")
        db.session.add(med)
        med=Medicine(med_id="05",med_name="Zyrtec")
        db.session.add(med)
        med=Medicine(med_id="06",med_name="Tavist-D")
        db.session.add(med)
        med=Medicine(med_id="07",med_name="Tylenol")
        db.session.add(med)
        med=Medicine(med_id="08",med_name="Aspirin")
        db.session.add(med)
        med=Medicine(med_id="09",med_name="Phenobarbital")
        db.session.add(med)
        med=Medicine(med_id="10",med_name="Valproic Acid")
        db.session.add(med)
        med=Medicine(med_id="11",med_name="Insulin")
        db.session.add(med)
        med=Medicine(med_id="12",med_name="Glucotrol")
        db.session.add(med)


        effects=MedicineEffects(med_id="01",med_effects="Nausea")
        db.session.add(effects)
        effects=MedicineEffects(med_id="01",med_effects="Rash")
        db.session.add(effects)
        effects=MedicineEffects(med_id="02",med_effects="Yeast Infections")
        db.session.add(effects)
        effects=MedicineEffects(med_id="02",med_effects="Fever")
        db.session.add(effects)
        effects=MedicineEffects(med_id="02",med_effects="Diarrhea")
        db.session.add(effects)
        effects=MedicineEffects(med_id="03",med_effects="Nervous Feeling")
        db.session.add(effects)
        effects=MedicineEffects(med_id="03",med_effects="Vomiting")
        db.session.add(effects)
        effects=MedicineEffects(med_id="04",med_effects="Sweating")
        db.session.add(effects)
        effects=MedicineEffects(med_id="04",med_effects="Nausea")
        db.session.add(effects)
        effects=MedicineEffects(med_id="05",med_effects="Drowsiness")
        db.session.add(effects)
        effects=MedicineEffects(med_id="06",med_effects="Insomnia")
        db.session.add(effects)
        effects=MedicineEffects(med_id="06",med_effects="Weakness")
        db.session.add(effects)
        effects=MedicineEffects(med_id="07",med_effects="Nausea")
        db.session.add(effects)
        effects=MedicineEffects(med_id="07",med_effects="Tinnitus")
        db.session.add(effects)
        effects=MedicineEffects(med_id="07",med_effects="Stomach Upset")
        db.session.add(effects)
        effects=MedicineEffects(med_id="08",med_effects="Nausea")
        db.session.add(effects)
        effects=MedicineEffects(med_id="08",med_effects="Tinnitus")
        db.session.add(effects)
        effects=MedicineEffects(med_id="08",med_effects="Stomach Upset")
        db.session.add(effects)
        effects=MedicineEffects(med_id="09",med_effects="Dizziness")
        db.session.add(effects)
        effects=MedicineEffects(med_id="09",med_effects="Drowsiness")
        db.session.add(effects)
        effects=MedicineEffects(med_id="09",med_effects="Fainting")
        db.session.add(effects)
        effects=MedicineEffects(med_id="10",med_effects="Dizziness")
        db.session.add(effects)
        effects=MedicineEffects(med_id="10",med_effects="Drowsiness")
        db.session.add(effects)
        effects=MedicineEffects(med_id="11",med_effects="Nausea")
        db.session.add(effects)
        effects=MedicineEffects(med_id="11",med_effects="Heartburn")
        db.session.add(effects)
        effects=MedicineEffects(med_id="11",med_effects="Fatigue")
        db.session.add(effects)
        effects=MedicineEffects(med_id="12",med_effects="Nausea")
        db.session.add(effects)
        effects=MedicineEffects(med_id="12",med_effects="Heartburn")
        db.session.add(effects)
        effects=MedicineEffects(med_id="12",med_effects="Fatigue")
        db.session.add(effects)
        




        medclass=MedicineClass(med_id="01",med_class="Antibiotics")
        db.session.add(medclass)
        medclass=MedicineClass(med_id="02",med_class="Antibiotics")
        db.session.add(medclass)
        medclass=MedicineClass(med_id="03",med_class="Anti-Asthma Agents")
        db.session.add(medclass)
        medclass=MedicineClass(med_id="04",med_class="Anti-Asthma Agents")
        db.session.add(medclass)
        medclass=MedicineClass(med_id="05",med_class="Antihistamines")
        db.session.add(medclass)
        medclass=MedicineClass(med_id="06",med_class="Antihistamines")
        db.session.add(medclass)
        medclass=MedicineClass(med_id="07",med_class="Analgesics")
        db.session.add(medclass)
        medclass=MedicineClass(med_id="08",med_class="Analgesics")
        db.session.add(medclass)
        medclass=MedicineClass(med_id="09",med_class="Anticonvulsants")
        db.session.add(medclass)
        medclass=MedicineClass(med_id="09",med_class="Antiepileptic")
        db.session.add(medclass)
        medclass=MedicineClass(med_id="10",med_class="Anticonvulsants")
        db.session.add(medclass)
        medclass=MedicineClass(med_id="10",med_class="Antiepileptic")
        db.session.add(medclass)
        medclass=MedicineClass(med_id="11",med_class="Antidiabetics")
        db.session.add(medclass)
        medclass=MedicineClass(med_id="12",med_class="Antidiabetics")
        db.session.add(medclass)
        db.session.commit()

        adminemail=UserEmail(email_id="admin1@gmail.com",password="admin1")
        db.session.add(adminemail)
        adminidentity=UserIdentity(UniqueID="000000000000",user_name="ADMIN 1",mobile="0000000000")
        db.session.add(adminidentity)
        admin=users(id="ADM1",email_id="admin1@gmail.com",UniqueID="00000000000000")
        db.session.add(admin)
        adminaddress=UserAddress(id="ADM1",DoorNo="admin",Street="admin",Area="admin",City="admin",State="admin",Pincode="000000")
        db.session.add(adminaddress)
        admin=Admins(admin_id="ADM1",admin_desig="manager")
        db.session.add(admin)
        db.session.commit()
    

if __name__=="__main__":
    from werkzeug.middleware.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[5])
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    medinit()
    app.jinja_env.cache = {}
    app.run(debug=True)