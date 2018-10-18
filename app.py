import os
from flask import Flask,request,abort,render_template,session,redirect,url_for,flash
from flask_bootstrap import Bootstrap
from flask_moment import  Moment
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,PasswordField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_mail import Message
from werkzeug.security import generate_password_hash,check_password_hash
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
#密码加密相关
app.config['SECRET_KEY'] = 'HARD TO GUESS FUCKING STRING'

#数据库相关
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///' + os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


#发送邮件设置
app.config['MAIL_SERVER'] = 'smtp.qq.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USERNAME'] = '3339120082@qq.com'
app.config['MAIL_PASSWORD'] = 'pmswcpcdyhgbdaga'
mail = Mail(app)




bootstrap = Bootstrap(app)
moment = Moment(app)


class NameForm(FlaskForm):
    name = StringField('你叫啥？',validators=[DataRequired()])
    password = PasswordField('密码',validators=[DataRequired()])
    submit = SubmitField('提交')

class Role():

    def __repr__(self):
        return '<Role %r>' % self.name


class User():
    __tablename__ = 'users'


    @property
    def password(self):
        raise AttributeError('密码不可读取')

    @password.setter
    def password(self,password):
        self.pass_hash = generate_password_hash(password)

    def verify_pass(self,password):
        return check_password_hash(self.pass_hash,password)


    def __repr__(self):
        return '<User %r>' % self.username


@app.route('/',methods=['GET','POST'])
def hello_world():
    # ug = request.headers.get("User-Agent")
    #db.create_all()
    #admin_role = Role.query.filter_by(name='damen').first()
    #userjohn = User(username='john12', role=admin_role)
    #db.session.add(admin_role)
    #db.session.add(userjohn)
    #db.session.add_all([admin_role,userjohn])
    #db.session.commit()
    #print(admin_role.id)
    #print(userjohn.id)
   # admin_role.name='da'
    #db.session.add(admin_role)
    #db.session.commit()
    #print(User.query.filter_by(role=admin_role))
    #db.session.delete(admin_role)
    #db.session.commit()
    name = None
    form = NameForm()
    if form.validate_on_submit():
        oldname = session.get('name')
        user = User.query.filter_by(username=form.name.data).first()
        if oldname is not None and oldname != form.name.data:
            flash('改名了大兄弟？')
        if user is None:
            user = User(username=form.name.data,fuck=1000)
            session['known'] = False
        else:
            session['known'] = True
        name = form.name.data
        session['name'] = name
        form.name.data = ''
        return redirect(url_for('hello_world'))
    return render_template('index.html',current_time=datetime.utcnow(),name=session.get('name'),form=form,known= session.get('known',False))

@app.route('/ok/')
def test():
    u = User()
    u.password = 'damen'
    #print(u.password)
    print(u.pass_hash)
    print(u.verify_pass('damen'))
   # print(u.verify_pass('ok'))

    u1 = User()
    u1.password = 'damen'
    print(u1.pass_hash)
    return '测试啦'
@app.route('/index/<name>/')
def index(name):
    msg = Message(subject='你好damen！', sender='3339120082@qq.com', recipients=['250115313@qq.com'])
    msg.body='sended by FatTiger'
    msg.html='<h1>测试发邮件<h1>'
    mail.send(msg)
    return render_template('user.html',name = name)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404


@app.errorhandler(500)
def inner_err(e):
    return render_template('500.html'),404

if __name__ == '__main__':
    app.run(debug=True)
