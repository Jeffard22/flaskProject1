from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)
app.secret_key = "supersecretkey"  # нужен для хранения сессий

# Настройка базы (SQLite файл messages.db в папке проекта)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///messages.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Модель (таблица)
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Message {self.id} {self.name}>"


# 📌 login manager
login_manager = LoginManager(app)
login_manager.login_view = "login"  # если пользователь не авторизован — редирект на /login


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


# 📌 Flask-Login требует функцию загрузки пользователя
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():  # put application's code here
    return render_template("index.html")


@app.route('/about')
def about():
    return render_template('about.html')


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        message = request.form["message"]

        # Создаем объект и сохраняем в БД
        new_msg = Message(name=name, email=email, message=message)
        try:
            db.session.add(new_msg)
            db.session.commit()
            return render_template("contact.html", success=True)
        except Exception as e:
            print("Ошибка:", e)
            return render_template("contact.html", success=False)
    return render_template("contact.html", success=False)


@app.route("/messages")
def messages():
    all_msgs = Message.query.order_by(Message.date.desc()).all()
    return render_template("messages.html", messages=all_msgs)


# Админка
admin = Admin(app, name="My Admin", template_mode="bootstrap4")

admin.add_view(ModelView(Message, db.session))
admin.add_view(ModelView(User, db.session))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # создаём таблицы при первом запуске
    app.run(host="0.0.0.0", port=5000)
