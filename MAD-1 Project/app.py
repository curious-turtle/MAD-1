from jinja2 import Template
from flask import Flask,render_template,request,redirect
from flask_sqlalchemy import SQLAlchemy

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
db=SQLAlchemy()
db.init_app(app)
app.app_context().push()


class Venue(db.Model):
    __tablename__='venue'
    venue_id=db.Column(db.Integer,autoincrement=True, primary_key=True)
    venue_name=db.Column(db.String,nullable=False)
    venue_place=db.Column(db.String,nullable=False)
    venue_location=db.Column(db.String,nullable=False)
    venue_capacity=db.Column(db.Integer,nullable=False)
    venue_show_relationship=db.relationship("Show",secondary="reservation")

class Show(db.Model):
    __tablename__='show'
    show_id=db.Column(db.Integer, autoincrement=True, primary_key=True)
    show_name=db.Column(db.String,nullable=False)
    show_rating=db.Column(db.String)
    show_timing=db.Column(db.String)
    show_tags=db.Column(db.String)
    show_ticket_price=db.Column(db.Integer)
    show_bookings=db.relationship("User",secondary="bookings")    #define this relation with venue also see some yt video for ref

class Reservation(db.Model):
    __tablename__='reservation'
    reservation_id=db.Column(db.Integer, autoincrement=True, primary_key=True)
    rvenue_id=db.Column(db.Integer, db.ForeignKey("venue.venue_id"),nullable=False)
    rshow_id=db.Column(db.Integer, db.ForeignKey("show.show_id"),nullable=False)

class User(db.Model):
    __tablename__='user'
    user_id=db.Column(db.Integer,autoincrement=True, primary_key=True)
    user_name=db.Column(db.String,nullable=False)
    user_mailid=db.Column(db.String,nullable=False)
    user_password=db.Column(db.String,nullable=False)

class Bookings(db.Model):
    __tablename__='bookings'
    booking_id=db.Column(db.Integer, autoincrement=True, primary_key=True)
    bshow_id=db.Column(db.Integer, db.ForeignKey("show.show_id"),nullable=False)
    buser_id=db.Column(db.Integer, db.ForeignKey("user.user_id"),nullable=False)

@app.route("/", methods=["GET"])
def index():
    return render_template('index.html')

@app.route("/user_login", methods=["GET","POST"])
def user_login():
    if request.method == 'GET':
        return render_template('user_login.html')
    if request.method == 'POST':
        u_mail=request.form.get('u_mail')
        u_password=request.form.get('u_password')
        validation=User.query.filter_by(user_mailid=u_mail,user_password=u_password).first()
        if validation:
            user_id=validation.user_id
            return redirect(f"/user_dashboard/{user_id}")
        else:
            return render_template('user_login.html',placeholder="invalid login/password")

@app.route("/user_signup", methods=["GET","POST"])
def user_signup():
    if request.method == 'GET':
        return render_template('user_signup.html')
    if request.method == 'POST':
        u_name=request.form.get('u_name')
        u_mail=request.form.get('u_mail')
        u_password=request.form.get('u_password')
        u1=User(user_name=u_name,user_mailid=u_mail,user_password=u_password)
        db.session.add(u1)
        try:
            db.session.commit()
            return redirect('/user_login')
        except:
            db.session.rollback()
            return "something went wrong while creating user"

@app.route("/user_dashboard/<int:user_id>", methods=["GET"])
def user_dashboard(user_id):
    pass

@app.route("/user/<int:user_id>/create_booking", methods=["GET","POST"])
def create_booking():
    if request.method == 'GET':
        return render_template('user_booking.html')
    if request.method == 'POST':
        b_number=request.form.get('b_number')


@app.route("/admin_login", methods=["GET","POST"])
def admin_login():
    if request.method == 'GET':
        return render_template('admin_login.html')
    if request.method == 'POST':
        admin_email_input=request.form.get('email')
        admin_password_input=request.form.get('password')
        if admin_email_input=="admin@ticketshowapp.com" and admin_password_input=="admin@123":
            return redirect('/admin_dashboard')
        else:
            return render_template('admin_login.html',placeholder="invalid login/password")

@app.route("/admin_dashboard", methods=["GET"])
def admin_dashboard():
    curr_admin_dash,venue_name_id_pair,show_name_id_pair={},{},{}
    all_venues=Venue.query.all()
    #print(all_venues)
    for venu in all_venues:
        venue_id=venu.venue_id
        v_name=venu.venue_name
        #print(v_name)
        venue_name_id_pair[v_name]=venue_id
        if v_name not in curr_admin_dash:
                curr_admin_dash[v_name]=[]
        all_shows=Reservation.query.filter_by(rvenue_id=venue_id).all()
        for show in all_shows:
            show_id=show.rshow_id
            s_name=Show.query.filter_by(show_id=show_id).first()
            curr_admin_dash[v_name].append(s_name.show_name)
            show_name_id_pair[s_name.show_name]=show_id
    #print(curr_admin_dash)
    return render_template('admin_dashboard.html',curr_admin_dash=curr_admin_dash,
                           venue_name_id_pair=venue_name_id_pair,
                           show_name_id_pair=show_name_id_pair)

@app.route("/admin/create_venue", methods=["GET","POST"])
def admin_create_venue():
    if request.method == 'GET':
        return render_template('create_venue.html')
    if request.method == 'POST':
        v_name=request.form.get('v_name')
        v_place=request.form.get('v_place')
        v_location=request.form.get('v_location')
        v_capacity=request.form.get('v_capacity')
        s1 = Venue(venue_name=v_name,venue_place=v_place,
                   venue_location=v_location,venue_capacity=v_capacity)
        db.session.add(s1)
        try:
            db.session.commit()
            return redirect('/admin_dashboard')
        except:
            db.session.rollback()
            return "something went wrong while adding venue"

@app.route("/admin/<int:venue_id>/update_venue", methods=["GET","POST"])
def admin_update_venue(venue_id):
    if request.method == 'GET':
        venue_to_update=Venue.query.filter_by(venue_id=venue_id).first()
        return render_template('update_venue.html',
                               v_name=venue_to_update.venue_name,
                               v_place=venue_to_update.venue_place,
                               v_location=venue_to_update.venue_location,
                               venue_id=venue_id)
    if request.method == 'POST':
        venue_to_update=Venue.query.filter_by(venue_id=venue_id).first()
        venue_to_update.venue_capacity=request.form.get('v_capacity')
        try:
            db.session.commit()
            return redirect('/admin_dashboard')
        except:
            db.session.rollback()
            return "something went wrong while updating venue"

@app.route("/admin/<int:venue_id>/delete_venue", methods=["GET"])
def admin_delete_venue(venue_id):    
        venue_to_delete=Venue.query.filter_by(venue_id=venue_id).first()
        db.session.delete(venue_to_delete)
        db.session.commit()
        return redirect('/admin_dashboard')

@app.route("/admin/<int:venue_id>/add_show", methods=["GET","POST"])
def admin_add_show(venue_id):
    if request.method == 'GET':
        return render_template('add_show.html',venue_id=venue_id)
    if request.method == 'POST':
        s_name=request.form.get('s_name')
        s_rating=request.form.get('s_rating')
        s_timing=request.form.get('s_timing')
        s_tags=request.form.get('s_tags')
        s_price=request.form.get('s_price')
        s1 = Show(show_name=s_name,show_rating=s_rating,
                  show_timing=s_timing,show_tags=s_tags,
                  show_ticket_price=s_price)
        db.session.add(s1)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            return "something went wrong while creating show"
        last_show_id=Show.query.filter_by(show_id=s1.show_id).first()
        print(venue_id,last_show_id)
        r1=Reservation(rvenue_id=venue_id,rshow_id=last_show_id.show_id)
        db.session.add(r1)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            return "something went wrong while adding reservation"
        return redirect('/admin_dashboard')

@app.route("/admin/<int:show_id>/update_show", methods=["GET","POST"])
def admin_update_show(show_id):
    if request.method == 'GET':
        show_to_update=Show.query.filter_by(show_id=show_id).first()
        return render_template('update_show.html',
                               s_name=show_to_update.show_name,
                               show_id=show_id)
    if request.method == 'POST':
        show_to_update=Show.query.filter_by(show_id=show_id).first()
        show_to_update.show_rating=request.form.get('s_rating')
        show_to_update.show_timing=request.form.get('s_timing')
        show_to_update.show_tags=request.form.get('s_tags')
        show_to_update.show_ticket_price=request.form.get('s_price')
        try:
            db.session.commit()
            return redirect('/admin_dashboard')
        except:
            db.session.rollback()
            return "something went wrong while updating show"

@app.route("/admin/<int:show_id>/delete_show", methods=["GET"])
def admin_delete_show(show_id): 
    show_relation_to_delete=Reservation.query.filter_by(rshow_id=show_id).all()
    for Relation_show in show_relation_to_delete:
        db.session.delete(Relation_show)
        db.session.commit()    
    show_to_delete=Show.query.filter_by(show_id=show_id).first()
    db.session.delete(show_to_delete)
    db.session.commit()
    return redirect('/admin_dashboard')

if __name__=='__main__':
    app.run(debug=True)