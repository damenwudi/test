import  os
from .app import create_app,db
from flask import  render_template
from .models import User,Role
from itsdangerous import TimedJSONWebSignatureSerializer as s
app = create_app(os.getenv('FLASK_CONFIG' or 'default'))


@app.shell_context_processor
def make_shell_context():
    return dict(db=db,User=User,Role=Role)

@app.route('/')
def hello():
    return render_template('index.html')