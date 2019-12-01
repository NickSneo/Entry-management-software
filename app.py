from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mail import Mail, Message
from twilio.rest import Client

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'
db = SQLAlchemy(app)

app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'

app.config['MAIL_SERVER']= 'smtp.googlemail.com'
app.config['MAIL_PORT']= 587
app.config['MAIL_USE_TLS']= True
app.config['MAIL_USERNAME']= 'nischal.kakamessi@gmail.com'
app.config['MAIL_PASSWORD']= 'iitB@1106'

mail = Mail(app)


account_sid = "AC8407de57761bb1787cb4d5319c21d027"
auth_token  = "00ccc7068963ba42acda22b26123a386"
client = Client(account_sid, auth_token)


class Guest(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.Unicode(50), nullable = False)
    tel = db.Column(db.Integer, nullable = False)
    mail = db.Column(db.String(50), nullable = False)
    host_name = db.Column(db.Unicode(50), nullable=False)
    check_in = db.Column(db.DateTime(timezone = True), default = datetime.now())
    check_out = db.Column(db.DateTime(timezone=True))
    checked_in = db.Column(db.Integer)
    
    def __repr__ (self):
        return '<Task %r >' % self.id

class Host(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.Unicode(50), nullable = False)
    tel = db.Column(db.Integer, nullable = False)
    mail = db.Column(db.String(50), nullable = False)
    avail = db.Column(db.Unicode(3), default = 'Yes')
    addr = db.Column(db.String(100), nullable = False)

    def __repr__ (self):
        return '<Task %r >' % self.id

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/guest/', methods=['POST','GET'])
def guest():
    if request.method == 'POST':
        g_name = request.form['guest_name']
        g_tel = request.form['guest_tel']
        g_mail = request.form['guest_mail']
        h_name = request.form['host_select']
        g_chin = request.form['checkin_time']

        host = Host.query.filter_by(name=h_name).first()
        

        if g_chin :
            time_in =  g_chin
            time_processing = time_in.replace('T', '-').replace(':', '-').split('-')
            time_processing = [int(v) for v in time_processing]
            g_chin = datetime(*time_processing)
            checked_in = 0
        
        else:
            g_chin = datetime.now()
            checked_in = 1
            host.avail = 'No'

        new_task = Guest(name=g_name, tel=g_tel, mail=g_mail, host_name=h_name, check_in=g_chin, checked_in=checked_in)
        

        db.session.add(new_task)
        db.session.commit()
        msg = Message('Meeting Scheduled', sender='nischal.kakamessi@gmail.com', recipients=[host.mail])
        msg.body = ''' Dear {0} a meeting has been scheduled. 
        Name of the Visitor - {1}
        Phone no. {2}
        Email-Id - {3}
        Checkin Date {4}
        Checkin Time - {5}
        Happy Hosting!!!
        '''.format(h_name,g_name,g_tel,g_mail,g_chin.date(),g_chin.strftime("%H:%M"))
        mail.send(msg)

        # twilio account is suspended therefore removed this
        message = client.messages.create(
                    from_='+12562987434',
                     to='+91{0}'.format(host.tel),
                     body='''Dear {0},your guest is {1}\nphone-{2}\nEmail-Id {3}\nCheckinTime- {4}\nHappy Hosting'''.format(host.name,g_name,g_tel,g_mail,g_chin)                     
                 )
        return redirect('/guest')

    else:
        hosts = Host.query.order_by(Host.id).all()
        guests = Guest.query.order_by(Guest.check_in).all()
        return render_template('guest.html', hosts = hosts, guests = guests)


@app.route('/guestlist/')
def guestlist():
        hosts = Host.query.order_by(Host.id).all()
        guests = Guest.query.order_by(Guest.id).all()
        return render_template('guestlist.html', hosts = hosts, guests = guests)

@app.route('/host/', methods=['POST','GET'])
def host():
    if request.method == 'POST':
        h_name = request.form['host_name']
        h_tel = request.form['host_tel']
        h_mail = request.form['host_mail']
        h_avail = request.form['host_availability']
        h_addr = request.form['host_addr']
        new_task = Host(name=h_name, tel=h_tel, mail=h_mail, avail=h_avail, addr=h_addr)

        db.session.add(new_task)
        db.session.commit()
        return redirect('/host')

    else:
        hosts = Host.query.order_by(Host.id).all()
        return render_template('host.html', hosts = hosts)

@app.route('/hostlist/')
def hostlist():
        hosts = Host.query.order_by(Host.id).all()
        return render_template('hostlist.html', hosts = hosts)


@app.route('/guest/check_out/<int:id>') 
def check_out(id):
    gt_cout = Guest.query.get_or_404(id)
    gt_cout.check_out = datetime.now()
    host = Host.query.filter_by(name=gt_cout.host_name).first()
    host.avail = 'Yes'
        
    msg = Message('Meeting Ended', sender='nischal.kakamessi@gmail.com', recipients=[gt_cout.mail])
    msg.body = ''' Dear {0} your meeting has been ended. 
    Phone no. {1}
    Checked-in on {2} at {3}
    Checked-out at {4}
    Hosted by {5}
    Address Visited - {6}
    Thanks for your visit!!!
    '''.format(gt_cout.name,gt_cout.tel,gt_cout.check_in.date(),gt_cout.check_in.strftime("%H:%M"),gt_cout.check_out.strftime("%H:%M"),gt_cout.host_name,host.addr)
    mail.send(msg)
    
    db.session.delete(gt_cout)
    db.session.commit()
    return redirect('/guestlist')

@app.route('/guestlist/check_in/<int:id>') 
def check_in(id):
    gt_cin = Guest.query.get_or_404(id)
    if (datetime.now().date()== gt_cin.check_in.date()) and (datetime.now().strftime("%H:%M") > gt_cin.check_in.strftime("%H:%M")) :
        host = Host.query.filter_by(name=gt_cin.host_name ).first()
        if host.avail == 'Yes':
            gt_cin.checked_in = 1
            gt_cin.checkin_time = datetime.now()
            host.avail = 'No'
            msg = Message('Meeting Started', sender='nischal.kakamessi@gmail.com', recipients=[host.mail])
            msg.body = ''' Dear {0} your meeting has been Started. 
            Name of the Visitor - {1}
            Phone no. {2}
            Email-Id - {3}
            Checkin Date {4}
            Checkin Time - {5}
            Happy Hosting!!!
            '''.format(host.name,gt_cin.name,gt_cin.tel,gt_cin.mail,datetime.now().date(),datetime.now().strftime("%H:%M"))
            mail.send(msg)
            message = client.messages.create(
            from_='+12562987434',
            to='+91{0}'.format(host.tel),
            body='''Dear {0},your guest is {1}\nphone-{2}\nEmail-Id {3}\nCheckinTime- {4}\nHappy Hosting'''.format(host.name,g_name,g_tel,g_mail,g_chin)                     
            )
                
        else:
            flash('Checkin Unsuccessful.You are late, Host is busy now, Check-in later', 'danger')

    else:
        flash('Checkin Unsuccessful. Please checkin at your schduled time', 'danger')
        
    return redirect('/guestlist')

    # msg = Message('Meeting Ended', sender='nischal.kakamessi@gmail.com', recipients=[gt_cout.mail])
    # msg.body = ''' Dear {0} your meeting has been ended. 
    # Phone no. {1}
    # Checked-in on {2} at {3}
    # Checked-out at {4}
    # Hosted by {5}
    # Address Visited - {6}
    # Thanks for your visit!!!
    # '''.format(gt_cout.name,gt_cout.tel,gt_cout.check_in.date(),gt_cout.check_in.strftime("%H:%M"),gt_cout.check_out.strftime("%H:%M"),gt_cout.host_name,host.addr)
    # mail.send(msg)
    
      

@app.route('/host/delete/<int:id>') 
def delete(id):
    host_to_delete = Host.query.get_or_404(id)
    db.session.delete(host_to_delete)
    db.session.commit()
    return redirect('/host')

@app.route('/host_update/<int:id>', methods=['GET','POST']) 
def update(id):
    host_edit = Host.query.get_or_404(id)
    if request.method == 'POST':
        host_edit.name = request.form['host_name']
        host_edit.tel = request.form['host_tel']
        host_edit.mail = request.form['host_mail']
        host_edit.avail = request.form['host_availability']
        host_edit.addr = request.form['host_addr']
        db.session.commit()
        return redirect('/host')

    else:
        return render_template('host_update.html', host=host_edit)               

if __name__ == "__main__":
    app.run(debug=True)   

