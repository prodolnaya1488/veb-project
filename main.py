import datetime
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from data.products import Products
from data import db_session
from data.users import User
from forms.user import RegisterForm, LoginForm
from forms.products import ProductsForm
from werkzeug.exceptions import abort
from werkzeug.utils import redirect
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URL'] = 'sqlite:///shop.db'
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
# db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_session.global_init("db/shop.db")
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/shop')
def main_shop():
    db_session.global_init("db/shop.db")
    db_sess = db_session.create_session()
    # products = db_sess.query(Products).filter(Products.is_private != True)
    if current_user.is_authenticated:
        products = db_sess.query(Products).filter(
            (Products.user == current_user) | (Products.is_private != True))
    else:
        products = db_sess.query(Products).filter(Products.is_private != True)
    return render_template('main_shop.html', products=products)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def main():
    return render_template('about.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/products',  methods=['GET', 'POST'])
@login_required
def add_news():
    form = ProductsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        product = Products()
        product.title = form.title.data
        product.author = form.author.data
        product.content = form.content.data
        # photo
        product.is_private = form.is_private.data
        current_user.products.append(product)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/shop')
    return render_template('products.html', title='Добавление книги',
                           form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/product/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = ProductsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        prod = db_sess.query(Products).filter(Products.id == id,
                                          Products.user == current_user
                                          ).first()
        if prod:
            form.title.data = prod.title
            form.author.data = prod.author
            form.content.data = prod.content
            form.is_private.data = prod.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        prod = db_sess.query(Products).filter(Products.id == id,
                                          Products.user == current_user
                                          ).first()
        if prod:
            prod.title = form.title.data
            prod.author = form.author.data
            prod.content = form.content.data
            prod.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/shop')
        else:
            abort(404)
    return render_template('products.html',
                           title='Редактирование товара',
                           form=form
                           )


@app.route('/product_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    prod = db_sess.query(Products).filter(Products.id == id,
                                      Products.user == current_user
                                      ).first()
    if prod:
        db_sess.delete(prod)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/shop')


if __name__ == '__main__':
    db_session.global_init("db/shop.db")
    db_sess = db_session.create_session()
    # user = User()
    # user.name = "Пользователь 1"
    # user.about = "биография пользователя 1"
    # user.email = "email1@email.ru"
    # user.hashed_password = 'gfhjkm123'
    # db_sess.add(user)
    # db_sess.commit()
    #
    # user = User()
    # user.name = "Пользователь 2"
    # user.about = "биография пользователя 2"
    # user.email = "email2@email.ru"
    # user.hashed_password = 'gfhjkm321'
    # db_sess.add(user)
    # db_sess.commit()
    #
    # products = Products(title="Мы", author='Замятин', content="Интересная антиутопия",
    #             user_id=2, is_private=False)

    # products = Products(title="Преступление и наказание", author='Достоевский', content="Интересный роман",
    #                     user_id=1, is_private=False)

    # db_sess.add(products)
    # db_sess.commit()


    # тут с картинками была попытка
    # prod = db_sess.query(Products).filter(User.id == 2).first()
    # print(prod)
    # prod.photo = 'static/img_users/zamyatin-my.jpg'
    # prod.created_date = datetime.datetime.now()
    # db_sess.commit()

    app.run(port=8080, host='127.0.0.1', debug=True)