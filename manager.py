from flask_script import Manager,Shell
from app import create_app,db
import os

#这个有问题
app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager=Manager(app)


@manager.command
def test():
    """运行单元测试"""
    import unittest
    tests=unittest.TestLoader().discover('test')
    unittest.TextTestRunner(verbosity=2).run(tests)
