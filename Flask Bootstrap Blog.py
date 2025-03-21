import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired
from flask_ckeditor import CKEditor

app = Flask(__name__)
app.config["CKEDITOR_PKG_TYPE"] = "basic"
app.config["SECRET_KEY"] = "supersecretkey"

ckeditor = CKEditor(app)

# Функция для получения всех статей
def get_articles():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, image, content FROM articles")
    articles = {row[0]: {"title": row[1], "image": row[2], "content": row[3]} for row in cursor.fetchall()}
    conn.close()
    return articles

# Функция для получения одной статьи
def get_article(article_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT title, image, content, full_content FROM articles WHERE id = ?", (article_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"title": row[0], "image": row[1], "content": row[2], "full_content": row[3]}
    return None

# Форма для добавления/редактирования статьи
class ArticleForm(FlaskForm):
    title = StringField("Заголовок", validators=[DataRequired()])
    image = StringField("Название изображения", validators=[DataRequired()])
    content = TextAreaField("Краткое описание", validators=[DataRequired()])
    full_content = TextAreaField("Полный текст статьи", validators=[DataRequired()])
    submit = SubmitField("Сохранить")

# Главная страница
@app.route("/")
def home():
    return render_template("index.html")

# Список статей
@app.route("/blog")
def blog():
    return render_template("blog.html", articles=get_articles())

# Просмотр статьи
@app.route("/article/<int:article_id>")
def article(article_id):
    article = get_article(article_id)
    if not article:
        return "Статья не найдена", 404
    return render_template("article.html", article=article)

# Админ-панель: список статей
@app.route("/admin")
def admin():
    return render_template("admin.html", articles=get_articles())

# Добавление статьи
@app.route("/admin/add", methods=["GET", "POST"])
def add_article():
    form = ArticleForm()
    if form.validate_on_submit():
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO articles (title, image, content, full_content) VALUES (?, ?, ?, ?)",
                       (form.title.data, form.image.data, form.content.data, form.full_content.data))
        conn.commit()
        conn.close()
        flash("Статья успешно добавлена!", "success")
        return redirect(url_for("admin"))
    return render_template("edit_article.html", form=form, action="Добавить статью")

# Редактирование статьи
@app.route("/admin/edit/<int:article_id>", methods=["GET", "POST"])
def edit_article(article_id):
    article = get_article(article_id)
    if not article:
        return "Статья не найдена", 404

    form = ArticleForm(data=article)
    if form.validate_on_submit():
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE articles SET title=?, image=?, content=?, full_content=? WHERE id=?",
                       (form.title.data, form.image.data, form.content.data, form.full_content.data, article_id))
        conn.commit()
        conn.close()
        flash("Статья успешно обновлена!", "success")
        return redirect(url_for("admin"))
    return render_template("edit_article.html", form=form, action="Редактировать статью")

# Удаление статьи
@app.route("/admin/delete/<int:article_id>", methods=["POST"])
def delete_article(article_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM articles WHERE id=?", (article_id,))
    conn.commit()
    conn.close()
    flash("Статья удалена!", "danger")
    return redirect(url_for("admin"))

if __name__ == "__main__":
    app.run(debug=True)
