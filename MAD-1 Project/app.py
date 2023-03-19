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
    venue_address=db.Column(db.String,nullable=False)
    venue_city=db.Column(db.String,nullable=False)
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
    show_capacity=db.Column(db.Integer)
    show_tickets_sold=db.Column(db.Integer)
    show_collection=db.Column(db.Integer)
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
    buser_id=db.Column(db.Integer, db.ForeignKey("user.user_id"),nullable=False)
    bvenue_id=db.Column(db.Integer, db.ForeignKey("venue.venue_id"),nullable=False)
    bshow_id=db.Column(db.Integer, db.ForeignKey("show.show_id"),nullable=False)
    

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
    curr_user_dash=[]
    all_venues=Venue.query.all()
    user_name=User.query.filter_by(user_id=user_id).first()
    user_name=user_name.user_name
    #print(user_name)
    for venu in all_venues:
        venue_id,v_name=venu.venue_id,venu.venue_name
        venue_address,venue_city=venu.venue_address,venu.venue_city
        all_shows=Reservation.query.filter_by(rvenue_id=venue_id).all()
        #print(v_name)
        curr_venue_detail={}
        curr_venue_detail[(venue_id,v_name,venue_address,venue_city)]=[]
        for show in all_shows:
            show_id=show.rshow_id
            curr_show=Show.query.filter_by(show_id=show_id).first()
            curr_venue_detail[(venue_id,v_name,venue_address,venue_city)].append([curr_show.show_name,
                                                                                  curr_show.show_rating,
                                                                                  curr_show.show_timing,
                                                                                  curr_show.show_tags,
                                                                                  curr_show.show_ticket_price,
                                                                                  show_id
                                                                                  ])
        curr_user_dash.append(curr_venue_detail)
    #print(curr_user_dash)
    return render_template('user_dashboard.html',curr_user_dash=curr_user_dash,
                           user_name=user_name,user_id=user_id)

@app.route("/user/<int:user_id>/create_booking/<int:venue_id>/<int:show_id>", methods=["GET","POST"])
def create_booking(user_id,venue_id,show_id):
    if request.method == 'GET':
        user_name=User.query.filter_by(user_id=user_id).first()
        venue_to_disp=Venue.query.filter_by(venue_id=venue_id).first()
        show_to_disp=Show.query.filter_by(show_id=show_id).first()
        available_seats=show_to_disp.show_capacity
        address=venue_to_disp.venue_address
        city=venue_to_disp.venue_city
        timing=show_to_disp.show_timing
        ticket_price=show_to_disp.show_ticket_price
        show_name=show_to_disp.show_name
        user_name=user_name.user_name
        return render_template('create_booking.html',user_name=user_name,show_name=show_name,
                               available_seats=available_seats,address=address,
                               city=city,timing=timing,ticket_price=ticket_price,
                               venue_id=venue_id,show_id=show_id,user_id=user_id)
    if request.method == 'POST':
        b_number=request.form.get('b_number')
        user_name=User.query.filter_by(user_id=user_id).first()
        venue_to_disp=Venue.query.filter_by(venue_id=venue_id).first()
        show_to_disp=Show.query.filter_by(show_id=show_id).first()
        available_seats=show_to_disp.show_capacity
        address=venue_to_disp.venue_address
        city=venue_to_disp.venue_city
        timing=show_to_disp.show_timing
        ticket_price=show_to_disp.show_ticket_price
        show_name=show_to_disp.show_name
        user_name=user_name.user_name
        if int(b_number)>available_seats:
            return render_template('create_booking.html',user_name=user_name,show_name=show_name,
                               available_seats=available_seats,address=address,
                               city=city,timing=timing,ticket_price=ticket_price,
                               venue_id=venue_id,show_id=show_id,user_id=user_id,
                               message="Sorry not enough tickets available please try again")
        else:
            show_to_update=Show.query.filter_by(show_id=show_id).first()
            show_to_update.show_capacity=show_to_update.show_capacity-int(b_number)
            show_to_update.show_tickets_sold+=int(b_number)
            show_to_update.show_collection+=(int(b_number)*show_to_update.show_ticket_price)
            db.session.commit()
            b1=Bookings(buser_id=user_id,bvenue_id=venue_id,bshow_id=show_id)
            db.session.add(b1)
            db.session.commit()
            return redirect(f'/user_dashboard/{user_id}')

@app.route("/user/<int:user_id>/user_bookings", methods=["GET"])
def user_bookings(user_id):
    user_name=User.query.filter_by(user_id=user_id).first()
    user_name=user_name.user_name
    user_bookings=Bookings.query.filter_by(buser_id=user_id).all()
    user_bookings_to_disp=[]
    for user_book in user_bookings:
        venue_id=user_book.bvenue_id
        show_id=user_book.bshow_id
        show_name=(Show.query.filter_by(show_id=show_id).first()).show_name
        show_timing=(Show.query.filter_by(show_id=show_id).first()).show_timing
        show_venue_name=(Venue.query.filter_by(venue_id=venue_id).first()).venue_name
        show_address=(Venue.query.filter_by(venue_id=venue_id).first()).venue_address
        show_city=(Venue.query.filter_by(venue_id=venue_id).first()).venue_city
        user_bookings_to_disp.append([show_name,show_timing,show_venue_name,show_address,show_city])
    return render_template('user_booking.html',
                               user_bookings_to_disp=user_bookings_to_disp,
                               venue_id=venue_id,show_id=show_id,user_id=user_id,user_name=user_name)



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
    curr_admin_dash=[]
    all_venues=Venue.query.all()
    for venu in all_venues:
        venue_id,v_name=venu.venue_id,venu.venue_name
        venue_address,venue_city=venu.venue_address,venu.venue_city
        all_shows=Reservation.query.filter_by(rvenue_id=venue_id).all()
        curr_venue_detail={}
        curr_venue_detail[(venue_id,v_name,venue_address,venue_city)]=[]
        for show in all_shows:
            show_id=show.rshow_id
            s_name=Show.query.filter_by(show_id=show_id).first()
            curr_show=Show.query.filter_by(show_id=show_id).first()
            curr_venue_detail[(venue_id,v_name,venue_address,venue_city)].append([curr_show.show_name,
                                                                                  curr_show.show_rating,
                                                                                  curr_show.show_timing,
                                                                                  curr_show.show_tags,
                                                                                  curr_show.show_ticket_price,
                                                                                  show_id
                                                                                  ])
        curr_admin_dash.append(curr_venue_detail)
    #print(curr_admin_dash)
    return render_template('admin_dashboard.html',curr_admin_dash=curr_admin_dash)

@app.route("/admin/create_venue", methods=["GET","POST"])
def admin_create_venue():
    if request.method == 'GET':
        return render_template('create_venue.html')
    if request.method == 'POST':
        v_name=request.form.get('v_name')
        v_address=request.form.get('v_address')
        v_city=request.form.get('v_city')
        v_capacity=request.form.get('v_capacity')
        s1 = Venue(venue_name=v_name,venue_address=v_address,
                   venue_city=v_city,venue_capacity=v_capacity)
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
                               v_address=venue_to_update.venue_address,
                               v_city=venue_to_update.venue_city,
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
        s_capacity=(Venue.query.filter_by(venue_id=venue_id).first()).venue_capacity
        s1 = Show(show_name=s_name,show_rating=s_rating,
                  show_timing=s_timing,show_tags=s_tags,
                  show_ticket_price=s_price,show_tickets_sold=0,
                  show_capacity=s_capacity,show_collection=0)
        db.session.add(s1)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            return "something went wrong while creating show"
        last_show_id=Show.query.filter_by(show_id=s1.show_id).first()
        #print(venue_id,last_show_id)
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