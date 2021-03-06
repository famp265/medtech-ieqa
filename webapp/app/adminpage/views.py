from flask_admin import AdminIndexView, expose, BaseView
from wtforms import form, fields
from flask.ext.login import current_user, login_user
from flask import redirect, url_for, render_template, flash, request
from werkzeug.security import check_password_hash
from .forms import AdminLoginForm
from ..customer.forms import ResultForm
from .. import mongo
from ..models import Customer
from flask_admin.contrib.pymongo import ModelView

class AdminResult1View(ModelView):
    can_create = False
    column_list = ('program_id', 'result_id', 'entered_by', 'entered_at')
    column_sortable_list = ('program_id', 'result_id', 'entered_by', 'entered_at')
    form_columns = ('program_id', 'albumin', 'albumin_', 'uric', 'uric_')
    form = ResultForm
    # form_create_rules = ('program_id', 'albumin', 'albumin_', 'uric', 'uric_')

    def is_accessible(self):
        # user = mongo.db.admins.find_one({'email': current_user.email})
        if current_user.is_authenticated():
            return True


class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if current_user.is_authenticated():
            flash('Logged in successfully.')

        if(not current_user.is_authenticated()):
            flash('Login failed.')
            return redirect(url_for('.login_view'))
        return super(MyAdminIndexView, self).index()

    @expose('/login/', methods=['GET', 'POST'])
    def login_view(self):
        form = AdminLoginForm()
        if form.validate_on_submit():
            admin = mongo.db.admins.find_one({'email': form.email.data})
            if admin is not None and check_password_hash(admin['password'],
                    form.password.data):
                admin = Customer(admin['email'])
                login_user(admin, form.remember_me.data)
                return redirect(request.args.get('next') \
                        or url_for('.index'))
            else:
                flash('Admin account required.')
                form.email.data = ''
                form.password.data = ''
                return self.render('admin/login.html', form=form)
            flash('Invalid admin email or password.')
        return self.render('admin/login.html', form=form)

class HomeView(BaseView):
    @expose('/')
    def home(self):
        return redirect(url_for('main.index'))
