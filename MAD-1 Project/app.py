from jinja2 import Template
from flask import Flask,render_template,request,redirect
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource,Api,reqparse
import plotly.graph_objs as go
import plotly.io as pio

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
db=SQLAlchemy()
db.init_app(app)
app.app_context().push()
api=Api(app)

parser = reqparse.RequestParser()
parser.add_argument('v_name')
parser.add_argument('v_address')
parser.add_argument('v_city')
parser.add_argument('v_capacity')

parser.add_argument('s_name')
parser.add_argument('s_timing')
parser.add_argument('s_tags')
parser.add_argument('s_ticket_price')

class VenueApi(Resource):
    def get(self,venue_id):
        venue=db.session.query(Venue).filter(Venue.venue_id==venue_id).first()
        if venue:
            return {"Venue_id":venue.venue_id,"venue_name":venue.venue_name,
                    "venue_address":venue.venue_address,"venue_city":venue.venue_city,
                    "venue_capacity":venue.venue_capacity} ,201
        else:
            return {"status": "Venue not found"}, 404
    def put(self,venue_id):
        info = parser.parse_args()
        v_name_update=info.get("v_name",None)
        v_address_update=info.get("v_address",None)
        v_city_update=info.get("v_city",None)
        v_capacity_update=info.get("v_capacity",None)
        print(v_name_update)
        if (not (v_name_update and v_name_update.strip())):
            return {"error_message":"Venue Name is required"},400
        elif (not (v_address_update and v_address_update.strip())):
            return {"error_message":"Venue address is required"},400
        elif (not (v_city_update and v_city_update.strip())):
            return {"error_message":"Venue city is required"},400
        elif (not (v_capacity_update and v_capacity_update.strip())):
            return {"error_message":"Venue capacity is required"},400
        else:
            venue_to_update=Venue.query.filter_by(venue_id=venue_id).first()
            if venue_to_update:
                venue_to_update.venue_name=v_name_update
                venue_to_update.venue_address=v_address_update
                venue_to_update.venue_city=v_city_update
                venue_to_update.venue_capacity=v_capacity_update
                db.session.commit()
                venue=db.session.query(Venue).filter(Venue.venue_id==venue_id).first()
                return {"Venue_id":venue.venue_id,"venue_name":venue.venue_name,
                    "venue_address":venue.venue_address,"venue_city":venue.venue_city,
                    "venue_capacity":venue.venue_capacity} ,201
            else:
                return {"status": "Venue Not Found"}, 404 
    def delete(self,venue_id):
        venue_relation_to_delete=Reservation.query.filter_by(rvenue_id=venue_id).all()
        show_to_delete_based_on_reservation=[]
        for relation_venue in venue_relation_to_delete:
            show_to_delete_based_on_reservation.append(relation_venue.rshow_id)
            db.session.delete(relation_venue)
            db.session.commit()
        for show_to_delete in show_to_delete_based_on_reservation:
            show_to_delete=Show.query.filter_by(show_id=show_to_delete).first()
            db.session.delete(show_to_delete) 
            db.session.commit()
        venue_booking_to_delete=Bookings.query.filter_by(bvenue_id=venue_id).all()
        for booking_venue in venue_booking_to_delete:
            db.session.delete(booking_venue)
            db.session.commit()   
        venue_to_delete=Venue.query.filter_by(venue_id=venue_id).first()
        if venue_to_delete:
            db.session.delete(venue_to_delete)
            db.session.commit()
            return {"status": "Successfully Deleted"}, 200 
        else:
            return {"status": "Venue not found"}, 404
    def post(self):
        info = parser.parse_args()
        v_name=info.get("v_name",None)
        v_address=info.get("v_address",None)
        v_city=info.get("v_city",None)
        v_capacity=info.get("v_capacity",None)
        if (not (v_name and v_name.strip())):
            return {"error_message":"Venue Name is required"},400
        elif (not (v_address and v_address.strip())):
            return {"error_message":"Venue address is required"},400
        elif (not (v_city and v_city.strip())):
            return {"error_message":"Venue city is required"},400
        elif (not (v_capacity and v_capacity.strip())):
            return {"error_message":"Venue capacity is required"},400
        else:
            s1 = Venue(venue_name=v_name,venue_address=v_address,
                   venue_city=v_city,venue_capacity=v_capacity)
            db.session.add(s1)
            db.session.commit()
            all_venue=Venue.query.all()
            specific_venue=all_venue[-1]
            return {"Venue_id":specific_venue.venue_id,"venue_name":specific_venue.venue_name,
                    "venue_address":specific_venue.venue_address,"venue_city":specific_venue.venue_city,
                    "venue_capacity":specific_venue.venue_capacity} ,201

class ShowApi(Resource):
    def get(self,show_id):
        show=db.session.query(Show).filter(Show.show_id==show_id).first()
        if show:
            return {"Show_id":show.show_id,"show_name":show.show_name,
                    "show_rating":show.show_rating,"show_timing":show.show_timing,
                    "show_tags":show.show_tags,"show_ticket_price":show.show_ticket_price} ,201
        else:
            return {"status": "Show not found"}, 404
    def put(self,show_id):
        info = parser.parse_args()
        s_name_update=info.get("s_name",None)
        s_timing_update=info.get("s_timing",None)
        s_tags_update=info.get("s_tags",None)
        s_ticket_price_update=info.get("s_ticket_price",None)
        if (not (s_name_update and s_name_update.strip())):
            return {"error_message":"Show Name is required"},400
        elif (not (s_timing_update and s_timing_update.strip())):
            return {"error_message":"Show timing is required"},400
        elif (not (s_tags_update and s_tags_update.strip())):
            return {"error_message":"Show tags is required"},400
        elif (not (s_ticket_price_update and s_ticket_price_update.strip())):
            return {"error_message":"Show ticket price is required"},400
        else:
            show_to_update=db.session.query(Show).filter(Show.show_id==show_id).first()
            if show_to_update:
                show_to_update.show_name=s_name_update
                show_to_update.show_timing=s_timing_update
                show_to_update.show_tags=s_tags_update
                show_to_update.show_ticket_price=s_ticket_price_update
                db.session.commit()
                show=db.session.query(Show).filter(Show.show_id==show_id).first()
                return {"Show_id":show.show_id,"show_name":show.show_name,
                    "show_rating":show.show_rating,"show_timing":show.show_timing,
                    "show_tags":show.show_tags,"show_ticket_price":show.show_ticket_price} ,201
    def delete(self,show_id):
        show_relation_to_delete=Reservation.query.filter_by(rshow_id=show_id).all()
        for Relation_show in show_relation_to_delete:
            db.session.delete(Relation_show)
            db.session.commit()
        show_booking_to_delete=Bookings.query.filter_by(bshow_id=show_id).all()
        for booking_show in show_booking_to_delete:
            db.session.delete(booking_show)
            db.session.commit()    
        show_to_delete=db.session.query(Show).filter(Show.show_id==show_id).first()
        if show_to_delete:
            db.session.delete(show_to_delete)
            db.session.commit()
            return {"status": "Successfully Deleted"}, 200 
        else:
            return {"status": "Show not found"}, 404
    def post(self,venue_id):
        info = parser.parse_args()
        s_name=info.get("s_name",None)
        s_timing=info.get("s_timing",None)
        s_tags=info.get("s_tags",None)
        s_ticket_price=info.get("s_ticket_price",None)
        print(s_name)
        s_capacity=(Venue.query.filter_by(venue_id=venue_id).first()).venue_capacity
        if (not (s_name and s_name.strip())):
            return {"error_message":"Show Name is required"},400
        elif (not (s_timing and s_timing.strip())):
            return {"error_message":"Show timing is required"},400
        elif (not (s_tags and s_tags.strip())):
            return {"error_message":"Show tags is required"},400
        elif (not (s_ticket_price and s_ticket_price.strip())):
            return {"error_message":"Show ticket price is required"},400
        else:
            s1 = Show(show_name=s_name,show_timing=s_timing,show_tags=s_tags,show_ticket_price=s_ticket_price,
                      show_tickets_sold=0,show_capacity=s_capacity,show_collection=0)
            db.session.add(s1)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            return {"error_message":"Rollback error"},500
        last_show_id=Show.query.filter_by(show_id=s1.show_id).first()
        r1=Reservation(rvenue_id=venue_id,rshow_id=last_show_id.show_id)
        db.session.add(r1)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            return {"error_message":"Rollback error"},500
        show=Show.query.filter_by(show_id=s1.show_id).first()
        if show:
            return {"Show_id":show.show_id,"show_name":show.show_name,
                    "show_rating":show.show_rating,"show_timing":show.show_timing,
                    "show_tags":show.show_tags,"show_ticket_price":show.show_ticket_price} ,201
        else:
            return {"status": "Show not found"}, 404

class Venue(db.Model):
    __tablename__='venue'
    venue_id=db.Column(db.Integer,autoincrement=True, primary_key=True)
    venue_name=db.Column(db.String,nullable=False)
    venue_address=db.Column(db.String,nullable=False)
    venue_city=db.Column(db.String,nullable=False)
    venue_capacity=db.Column(db.Integer,nullable=False)
    #venue_show_relationship=db.relationship("Show",secondary="reservation")

class Show(db.Model):
    __tablename__='show'
    show_id=db.Column(db.Integer, autoincrement=True, primary_key=True)
    show_name=db.Column(db.String,nullable=False)
    show_rating=db.Column(db.Integer)
    show_timing=db.Column(db.String)
    show_tags=db.Column(db.String)
    show_ticket_price=db.Column(db.Integer)
    show_capacity=db.Column(db.Integer)
    show_tickets_sold=db.Column(db.Integer)
    show_collection=db.Column(db.Integer)
    #show_bookings=db.relationship("User",secondary="bookings")    #define this relation with venue also see some yt video for ref

class Reservation(db.Model):
    __tablename__='reservation'
    reservation_id=db.Column(db.Integer, autoincrement=True, primary_key=True)
    rvenue_id=db.Column(db.Integer,nullable=False)
    rshow_id=db.Column(db.Integer,nullable=False)

class User(db.Model):
    __tablename__='user'
    user_id=db.Column(db.Integer,autoincrement=True, primary_key=True)
    user_name=db.Column(db.String,nullable=False)
    user_mailid=db.Column(db.String,nullable=False)
    user_password=db.Column(db.String,nullable=False)

class Bookings(db.Model):
    __tablename__='bookings'
    booking_id=db.Column(db.Integer, autoincrement=True, primary_key=True)
    buser_id=db.Column(db.Integer,nullable=False)
    bvenue_id=db.Column(db.Integer,nullable=False)
    bshow_id=db.Column(db.Integer,nullable=False)
    brating=db.Column(db.Integer)
    
api.add_resource(VenueApi,"/api/venue/<int:venue_id>","/api/venue")
api.add_resource(ShowApi,"/api/show/<int:show_id>","/api/<int:venue_id>/show")


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
        signup_validation=User.query.filter_by(user_mailid=u_mail).first()
        if signup_validation:
            return render_template('user_signup.html',placeholder="Email ID already exist")
        u1=User(user_name=u_name,user_mailid=u_mail,user_password=u_password)
        db.session.add(u1)
        try:
            db.session.commit()
            return redirect('/user_login')
        except:
            db.session.rollback()
            return "something went wrong while creating user"

@app.route("/user_dashboard/<int:user_id>", methods=["GET","POST"])
def user_dashboard(user_id):
    if request.method=='GET':
        curr_user_dash=[]
        search_by_tag=set()
        all_venues=Venue.query.all()
        user_name=User.query.filter_by(user_id=user_id).first()
        user_name=user_name.user_name
        for venu in all_venues:
            venue_id,v_name=venu.venue_id,venu.venue_name
            venue_address,venue_city=venu.venue_address,venu.venue_city
            all_shows=Reservation.query.filter_by(rvenue_id=venue_id).all()    
            curr_venue_detail={}
            curr_venue_detail[(venue_id,v_name,venue_address,venue_city)]=[]
            for show in all_shows:
                curr_show_rating=[]
                show_id=show.rshow_id
                all_shows_for_rating_cal=Bookings.query.filter_by(bshow_id=show_id).all()    
                for rating_cal in all_shows_for_rating_cal:
                    if rating_cal.brating:
                        curr_show_rating.append(rating_cal.brating)
                curr_show=Show.query.filter_by(show_id=show_id).first()
                if curr_show_rating:
                    curr_show.show_rating=sum(curr_show_rating)/len(curr_show_rating)
                    db.session.commit()
                search_by_tag.add(curr_show.show_tags)
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
                            user_name=user_name,user_id=user_id,search_by_tag=search_by_tag)
    if request.method == 'POST':
        search_by_tag_value=request.form['tags']
        curr_user_dash=[]
        search_by_tag=set()
        all_venues=Venue.query.all()
        user_name=User.query.filter_by(user_id=user_id).first()
        user_name=user_name.user_name
        for venu in all_venues:
            venue_id,v_name=venu.venue_id,venu.venue_name
            venue_address,venue_city=venu.venue_address,venu.venue_city
            all_shows=Reservation.query.filter_by(rvenue_id=venue_id).all()    
            curr_venue_detail={}
            curr_venue_detail[(venue_id,v_name,venue_address,venue_city)]=[]
            curr_show_rating=[]
            for show in all_shows:
                show_id=show.rshow_id
                all_shows_for_rating_cal=Bookings.query.filter_by(bshow_id=show_id).all()    
                for rating_cal in all_shows_for_rating_cal:
                    if rating_cal.brating:
                        curr_show_rating.append(rating_cal.brating)
                curr_show=Show.query.filter_by(show_id=show_id).first()
                if curr_show_rating:
                    curr_show.show_rating=sum(curr_show_rating)/len(curr_show_rating)
                search_by_tag.add(curr_show.show_tags)
                if curr_show.show_tags==search_by_tag_value:
                    curr_venue_detail[(venue_id,v_name,venue_address,venue_city)].append([curr_show.show_name,
                                                                                    curr_show.show_rating,
                                                                                    curr_show.show_timing,
                                                                                    curr_show.show_tags,
                                                                                    curr_show.show_ticket_price,
                                                                                    show_id
                                                                                    ])
            curr_user_dash.append(curr_venue_detail)
        return render_template('user_dashboard.html',curr_user_dash=curr_user_dash,
                            user_name=user_name,user_id=user_id,search_by_tag=search_by_tag)

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
            already_have_ticekts=Bookings.query.filter_by(buser_id=user_id,bvenue_id=venue_id,bshow_id=show_id).first()
            if not already_have_ticekts:
                b1=Bookings(buser_id=user_id,bvenue_id=venue_id,bshow_id=show_id)
                db.session.add(b1)
                db.session.commit()
            return redirect(f'/user_dashboard/{user_id}')

@app.route("/user/<int:user_id>/user_bookings", methods=["GET"])
def user_bookings(user_id):
    rating_bar=[1,2,3,4,5]
    user_name=User.query.filter_by(user_id=user_id).first()
    user_name=user_name.user_name
    user_bookings=Bookings.query.filter_by(buser_id=user_id).all()
    user_bookings_to_disp=[]
    if(not user_bookings):
        return render_template('user_booking.html',user_bookings_to_disp=user_bookings_to_disp,
                            user_name=user_name,user_id=user_id)    
    for user_book in user_bookings:
        venue_id=user_book.bvenue_id
        show_id=user_book.bshow_id
        rating=user_book.brating
        show_name=(Show.query.filter_by(show_id=show_id).first()).show_name
        show_timing=(Show.query.filter_by(show_id=show_id).first()).show_timing
        show_venue_name=(Venue.query.filter_by(venue_id=venue_id).first()).venue_name
        show_address=(Venue.query.filter_by(venue_id=venue_id).first()).venue_address
        show_city=(Venue.query.filter_by(venue_id=venue_id).first()).venue_city
        user_bookings_to_disp.append([show_name,show_timing,show_venue_name,show_address,show_city,rating,venue_id,show_id])
    return render_template('user_booking.html',
                            user_bookings_to_disp=user_bookings_to_disp,user_id=user_id,
                            user_name=user_name,rating_bar=rating_bar)

@app.route("/user/<int:user_id>/<int:venue_id>/<int:show_id>/rating", methods=["POST"])
def user_rating(user_id,venue_id,show_id):
    find_user_for_rating=Bookings.query.filter_by(buser_id=user_id,bvenue_id=venue_id,bshow_id=show_id).first()
    find_user_for_rating.brating=int(request.form['rating'])
    db.session.commit()
    curr_show_rating=[]
    all_shows_for_rating_cal=Bookings.query.filter_by(bshow_id=show_id).all()    
    for rating_cal in all_shows_for_rating_cal:
        if rating_cal.brating:
            curr_show_rating.append(rating_cal.brating)
    curr_show=Show.query.filter_by(show_id=show_id).first()
    if curr_show_rating:
        curr_show.show_rating=sum(curr_show_rating)/len(curr_show_rating)
        db.session.commit()
    return redirect(f"/user/{user_id}/user_bookings")

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
            curr_show_rating=[]
            show_id=show.rshow_id
            all_shows_for_rating_cal=Bookings.query.filter_by(bshow_id=show_id).all()    
            for rating_cal in all_shows_for_rating_cal:
                if rating_cal.brating:
                    curr_show_rating.append(rating_cal.brating)
            curr_show=Show.query.filter_by(show_id=show_id).first()
            if curr_show_rating:
                curr_show.show_rating=sum(curr_show_rating)/len(curr_show_rating)
                db.session.commit()
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
        venue_relation_to_delete=Reservation.query.filter_by(rvenue_id=venue_id).all()
        show_to_delete_based_on_reservation=[]
        for relation_venue in venue_relation_to_delete:
            show_to_delete_based_on_reservation.append(relation_venue.rshow_id)
            db.session.delete(relation_venue)
            db.session.commit()
        for show_to_delete in show_to_delete_based_on_reservation:
            show_to_delete=Show.query.filter_by(show_id=show_to_delete).first()
            db.session.delete(show_to_delete) 
            db.session.commit()
        venue_booking_to_delete=Bookings.query.filter_by(bvenue_id=venue_id).all()
        for booking_venue in venue_booking_to_delete:
            db.session.delete(booking_venue)
            db.session.commit()   
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
        #s_rating=request.form.get('s_rating')
        s_timing=request.form.get('s_timing')
        s_tags=request.form.get('s_tags')
        s_price=request.form.get('s_price')
        s_capacity=(Venue.query.filter_by(venue_id=venue_id).first()).venue_capacity
        s1 = Show(show_name=s_name,show_timing=s_timing,show_tags=s_tags,
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
    show_booking_to_delete=Bookings.query.filter_by(bshow_id=show_id).all()
    for booking_show in show_booking_to_delete:
        db.session.delete(booking_show)
        db.session.commit()    
    show_to_delete=Show.query.filter_by(show_id=show_id).first()
    db.session.delete(show_to_delete)
    db.session.commit()
    return redirect('/admin_dashboard')

@app.route("/admin/generate_report", methods=["GET"])
def generate_report():
    all_shows=Show.query.all()
    ticket_sold={}
    collection={}
    rating={}
    movie_rating=[]
    for show in all_shows:
        if show.show_name not in ticket_sold:
            ticket_sold[show.show_name]=0                       #tickets_sold
        ticket_sold[show.show_name]+=show.show_tickets_sold
        if show.show_name not in collection:
            collection[show.show_name]=0                        #collection
        collection[show.show_name]+=show.show_collection
        if show.show_name not in rating:
            rating[show.show_name]=[]                        #rating
        rating[show.show_name].append(show.show_rating)


    movies=list(ticket_sold.keys())
    ticket_sold_value=list(ticket_sold.values())
    movie_collection=list(collection.values())
    for rate in rating.values():
        rating_sum,rating_count=0,0
        for val in rate:
            if val:
                rating_sum+=val
                rating_count+=1
                movie_rating=[rating_sum/rating_count]


    if not movies:
        return "No shows added yet"
    if not ticket_sold_value or not movie_collection:
        return "No ticekts sold so far"
    
    data = go.Bar(x=movies, y=ticket_sold_value)
    layout = go.Layout(title='Tickets Sold')
    fig = go.Figure(data=[data], layout=layout)
    pio.write_image(fig, './static/movies_ticket.png')

    data = go.Bar(x=movies, y=movie_collection)
    layout = go.Layout(title='Box_office_collection')
    fig = go.Figure(data=[data], layout=layout)
    pio.write_image(fig, './static/movies_collection.png')

    data = go.Bar(x=movies, y=movie_rating)
    layout = go.Layout(title='Movie_rating')
    fig = go.Figure(data=[data], layout=layout)
    pio.write_image(fig, './static/movies_rating.png')

    return render_template('admin_report.html')

if __name__=='__main__':
    app.run(debug=True)