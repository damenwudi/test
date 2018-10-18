from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,BooleanField,PasswordField
from wtforms.validators import DataRequired,Length,Email,Regexp,EqualTo
from wtforms import  ValidationError
from ..models import User


class LoginForm(FlaskForm):
    #name = StringField('用户名:', validators=[DataRequired()])
    email = StringField('邮箱:',validators=[DataRequired(),Length(1,64),Email()])
    password = PasswordField('密码:',validators=[DataRequired()])
    remember_me = BooleanField('记住账号')
    submit = SubmitField('登录')


class ChangeForm(FlaskForm):
    #name = StringField('用户名:', validators=[DataRequired()])
    pc = PasswordField('密码:', validators=[DataRequired(), EqualTo('pc2', message='两个密码必须一致')])
    pc2 = PasswordField('确认密码:', validators=[DataRequired()])
    submit = SubmitField('修改')


#重置密码
class ResetForm(FlaskForm):
    #name = StringField('用户名:', validators=[DataRequired()])
    resetpass = StringField('请输入注册账号或者邮箱:', validators=[DataRequired()])
    submit = SubmitField('重置')

    def validate_resetpass(self,field):
        if not User.query.filter_by(email=field.data).first() and not User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名或邮箱还未注册!')


class RegistrationForm(FlaskForm):
    email = StringField('邮箱:', validators=[DataRequired(), Length(1, 64), Email()])
    username =  StringField('用户名:', validators=[DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,'用户名只能由字母、数字、点号和下划线组成，且必须以字母开头。')])
    password = PasswordField('密码:', validators=[DataRequired(),EqualTo('password2',message='两个密码必须一致')])
    password2 = PasswordField('确认密码:',validators=[DataRequired()])
    submit = SubmitField('注册')

    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已经被注册!')

    def validate_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已经被注册!')