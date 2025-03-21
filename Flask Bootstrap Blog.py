import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, FileField
from wtforms.validators import DataRequired
from flask_ckeditor import CKEditor
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["CKEDITOR_PKG_TYPE"] = "basic"
app.config["SECRET_KEY"] = "supersecretkey"
app.config["UPLOAD_FOLDER"] = "static/uploads"

ckeditor = CKEditor(app)

# Создаём папку, если её нет
if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])

# ✅ Функция для получения всех статей
def get_articles():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, image, content FROM articles")
    articles = [
        {"id": row[0], "title": row[1], "image": row[2], "content": row[3]}
        for row in cursor.fetchall()
    ]
    conn.close()
    return articles



# ✅ Функция для получения одной статьи (ОТСУТСТВОВАЛА!)
def get_article(article_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT title, image, content, full_content FROM articles WHERE id = ?", (article_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"title": row[0], "image": row[1], "content": row[2], "full_content": row[3]}
    return None

# ✅ Форма для добавления/редактирования статьи
class ArticleForm(FlaskForm):
    title = StringField("Заголовок", validators=[DataRequired()])
    image = FileField("Загрузить изображение (если новое)")
    content = TextAreaField("Краткое описание", validators=[DataRequired()])
    full_content = TextAreaField("Полный текст статьи", validators=[DataRequired()])
    submit = SubmitField("Сохранить")

# ✅ Главная страница
@app.route("/")
def home():
    return render_template("index.html")

# ✅ Список статей
@app.route("/blog")
def blog():
    return render_template("blog.html", articles=get_articles())

# ✅ Просмотр статьи
@app.route("/article/<int:article_id>")
def article(article_id):
    article = get_article(article_id)
    if not article:
        return "Статья не найдена", 404
    return render_template("article.html", article=article)

# ✅ Админ-панель: список статей
@app.route("/admin")
def admin():
    return render_template("admin.html", articles=get_articles())

# ✅ Загрузка изображения
@app.route("/upload", methods=["POST"])
def upload_image():
    if "upload" not in request.files:
        return {"error": "No file uploaded"}, 400

    file = request.files["upload"]
    if file.filename == "":
        return {"error": "No file selected"}, 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(file_path)

    file_url = url_for("static", filename="uploads/" + filename, _external=True)
    return {"uploaded": 1, "fileName": filename, "url": file_url}

# ✅ Добавление статьи с загрузкой изображения
@app.route("/admin/add", methods=["GET", "POST"])
def add_article():
    form = ArticleForm()
    image_filename = None  # ✅ Переменная для хранения имени изображения

    if form.validate_on_submit():
        if form.image.data:  # ✅ Проверяем, загружено ли изображение
            image = form.image.data
            image_filename = secure_filename(image.filename)  # ✅ Безопасное имя файла
            image_path = os.path.join(app.config["UPLOAD_FOLDER"], image_filename)
            image.save(image_path)  # ✅ Сохраняем файл в `static/uploads`

        # ✅ Добавляем статью в базу данных
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO articles (title, image, content, full_content) VALUES (?, ?, ?, ?)",
                       (form.title.data, image_filename, form.content.data, form.full_content.data))
        conn.commit()
        conn.close()

        flash("Статья успешно добавлена!", "success")
        return redirect(url_for("admin"))

    return render_template("edit_article.html", form=form, action="Добавить статью")

# ✅ Редактирование статьи
@app.route("/admin/edit/<int:article_id>", methods=["GET", "POST"])
def edit_article(article_id):
    article = get_article(article_id)
    if not article:
        return "Статья не найдена", 404

    form = ArticleForm(data=article)
    if form.validate_on_submit():
        image_filename = article["image"]  # Сохраняем старое изображение
        if form.image.data:
            image = form.image.data
            image_filename = secure_filename(image.filename)
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], image_filename))

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE articles SET title=?, image=?, content=?, full_content=? WHERE id=?",
                       (form.title.data, image_filename, form.content.data, form.full_content.data, article_id))
        conn.commit()
        conn.close()
        flash("Статья успешно обновлена!", "success")
        return redirect(url_for("admin"))

    return render_template("edit_article.html", form=form, action="Редактировать статью")

# ✅ Удаление статьи
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
