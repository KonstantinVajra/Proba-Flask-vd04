import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    image TEXT NOT NULL,
    content TEXT NOT NULL,
    full_content TEXT NOT NULL
)
""")

articles = [
    ("Деньги на Кубе", "money.jpg", "Официальная валюта Кубы – Кубинский песо (CUP).", "Кубинский песо является основной валютой страны. Также в ходу иностранная валюта: доллары США и евро. Лучшие курсы обмена можно найти у частных менял."),
    ("Погода на Кубе", "weather.jpg", "Куба имеет тропический климат с двумя сезонами.", "Сухой сезон (ноябрь – апрель) характеризуется мягкой температурой. Влажный сезон сопровождается высокой влажностью и ураганами.")
]

cursor.executemany("INSERT INTO articles (title, image, content, full_content) VALUES (?, ?, ?, ?)", articles)

conn.commit()
conn.close()
