from . import db
from werkzeug.security import  generate_password_hash,check_password_hash
from flask_login import UserMixin
from . import login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Se
from flask import  current_app


#这个地方把user对象传给current_user，current_user可以直接调用users表的字段
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin,db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64),unique=True,index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean,default=False)#是否经过邮件验证，默认为否


    # 确认安全令牌，这里要设置为静态方法
    @staticmethod
    def getUserid(token):
        s = Se(current_app.config['SECRET_KEY'])
        data = ''
        try:
            data = s.loads(token.encode('utf-8')).get('reset')
            #print('data:'+data)
        except:
            #print('data:' + data)
            return 0
        return data

    # 生成重设密码安全令牌,第一种方式
    def generate_reset_token(self, expiration=3600):
        s = Se(current_app.config['SECRET_KEY'], expiration)
        #print('id:'+str(self.id))
        return s.dumps({'reset': self.id}).decode('utf-8')

    # 生成重设密码安全令牌,第二种方式，不依赖于self，等于是独立的逻辑
    @staticmethod
    def generate_reset_token1(userid, expiration=3600):
        s = Se(current_app.config['SECRET_KEY'], expiration)
        # print('id:'+str(self.id))
        return s.dumps({'reset': userid}).decode('utf-8')

    #生成安全令牌
    def generate_confirm_token(self,expiration=360):
        s = Se(current_app.config['SECRET_KEY'],expiration)
        return s.dumps({'confirm':self.id}).decode('utf-8')

    #确认安全令牌
    def confirm(self,token):
        s = Se(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return  False
        self.confirmed = True
        db.session.add(self)
        return True


    #将password方法定义为一个属性，但是这个属性无法被读取
    @property
    def password(self):
        raise AttributeError('想读取密码是不可能的。')
    #生成hash值
    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)


    def check_pass(self,password):
        return  check_password_hash(self.password_hash,password)
    def __repr__(self):
        return '<User %r>' % self.username
