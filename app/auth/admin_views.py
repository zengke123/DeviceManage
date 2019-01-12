from flask_admin.contrib import sqla
import flask_login as login
from flask import redirect, url_for, request
from flask_admin import BaseView, expose


# admin身份验证，不是admin用户不允许访问 AdminModelView
class AdminModelView(sqla.ModelView):
    def is_accessible(self):
        if login.current_user.is_authenticated:
            return login.current_user.is_admin
        else:
            return False

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))


# admin页面添加返回主页视图
class IndexModelView(BaseView):
    @expose('/')
    def index(self):
        # Get URL for the test view method
        user_list_url = url_for('main.index')
        return self.render('index.html', user_list_url=user_list_url)