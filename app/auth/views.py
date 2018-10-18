from flask import  render_template,request,redirect,url_for,flash,session,g
from . import auth
from .forms import LoginForm
from ..models import  User
from flask_login import login_user,logout_user,login_required,current_user
from .forms import RegistrationForm,ChangeForm,ResetForm
from .. import  db
from ..email import send_email
from itsdangerous import TimedJSONWebSignatureSerializer as Se
from flask import  current_app

@auth.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.check_pass(form.password.data):
            login_user(user, form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('main.index')
            return redirect(next)
        flash('用户名或者密码输入有误！')
    return render_template('auth/login.html',form = form)



#重置密码
@auth.route('/resetpass',methods=['GET','POST'])
def resetpass():
    form = ResetForm()
    session['send'] = False
    if form.validate_on_submit():
        user = User()
        email = form.resetpass.data
        username = form.resetpass.data
        if username.find('@') > 0 :
            user = User.query.filter_by(email=email).first()
        else :
            user = User.query.filter_by(username=username).first()
            email = user.email
        #print('resetpass userid:'+str(user.id))

        #第一种生成token的方式，这个需要初始化user
        #token = user.generate_reset_token()

        #第二种生成token的方式，完全独立于user，不需要初始化
        token = User.generate_reset_token1(user.id)

        #users = User()
        #userid = User.getUserid(token)
        #
        # print(userid)
        #print(token)
        session['send'] = True
        send_email(email, '重置你的密码', 'auth/email/reset', user=user, token=token)
        flash('密码重置邮件已发送！')
        return redirect(url_for('auth.resetpass'))
    return render_template('auth/resetpass.html',form=form)


@auth.route('/rpage/<token>',methods=['GET','POST'])
def rpage(token):
    form = ChangeForm()
    userid = User.getUserid(token)
    #print(token)
    # s = Se(current_app.config['SECRET_KEY'])
    # data = ''
    #try:
    #     data = s.loads(token.encode('utf-8'))
    #     # print('data:'+data)
        #userid = userid.get('reset')
    #except:
        # print('data:' + data)
        # data =0
        #userid = 0
    #print(data)
    if userid is None or User.query.filter_by(id = userid).first() is None:
        return '<h1>链接已失效，请重新发起请求。</h1>'
    if form.validate_on_submit():
        #userid = User.getUserid(token).get('reset')
        user = User.query.filter_by(id = userid).first()
        user.password  = form.pc.data
        db.session.add(user)
        db.session.commit()
        flash('密码已重置请重新登录！')
        return redirect(url_for('auth.login'))
    return render_template('auth/changePassword.html',form=form)


#修改密码
@auth.route('/changePassword',methods=['GET','POST'])
@login_required
def changePassword():
    form = ChangeForm()
    if form.validate_on_submit():
        u = current_user
        u.password = form.pc.data
        db.session.add(u)
        db.session.commit()
        flash('密码修改成功！')
        return redirect(url_for('main.index'))
    return render_template('auth/changePassword.html',form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('你已经退出系统。')
    return render_template('auth/logout.html')

@auth.route('/check_email')
@login_required
def check_email():
    u = current_user
    if u.confirmed :
        session['check'] = True
        flash('你的账号已经激活，不需要重复确认。')
        return redirect(url_for('auth.unconfirm'))

    token = u.generate_confirm_token()
    send_email(u.email, '确认你的账户。。', 'auth/email/confirm', user=u, token=token)
    flash('一封确认账户的邮件已经发送到您的邮箱，请进邮箱确认。')
    return redirect(url_for('auth.unconfirm'))

@auth.route('/register',methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        u = User()
        u.username = form.username.data
        u.password = form.password.data
        u.email = form.email.data
        db.session.add(u)
        db.session.commit()
        login_user(u)
        # token = u.generate_confirm_token()
        # send_email(u.email,'确认你的账户。。','auth/email/confirm',user=u,token=token)
        # flash('一封确认账户的邮件已经发送到您的邮箱，请进邮箱确认。')
        return  redirect(url_for('auth.unconfirm'))
        # user = User.query.filter_by(email=form.email.data).first()
        # if user is not None and user.check_pass(form.password.data):
        #     login_user(user, form.remember_me.data)
        #     next = request.args.get('next')
        #     if next is None or not next.startswith('/'):
        #         next = url_for('main.index')
        #     return redirect(next)
        # flash('用户名或者密码输入有误！')
        #flash('注册成功！请登录。')
        #return redirect(url_for('auth.login'))
    return render_template('auth/register.html',form = form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        db.session.commit()
        flash('账号已经激活。')
    else:
        flash('无效的验证地址，请重新发送验证信息。')
    return  redirect(url_for('main.index'))


@auth.route('/unconfirm')
@login_required
def unconfirm():
    return render_template('auth/email/unconfirm.html')


@auth.before_app_request
def before_request():
    if current_user.is_authenticated and not current_user.confirmed  and request.blueprint !='auth' and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirm'))
    #return  render_template('index.html')
    # if current_user.is_anonymous or current_user.confirmed:
    #     return  redirect(url_for('main.index'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return  redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')
