import streamlit as st
import sqlite3
from PIL import Image
import io

# Подключение к базе данных SQLite (файл memes.db)
conn = sqlite3.connect('memes.db', check_same_thread=False)
cursor = conn.cursor()

# Создаем таблицу мемов, если не существует
cursor.execute('''
CREATE TABLE IF NOT EXISTS memes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image BLOB NOT NULL,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    votes INTEGER DEFAULT 0
)
''')
conn.commit()

st.title("Сайт для загрузки мемов и голосования")

# Форма загрузки мемов
with st.form("upload_form", clear_on_submit=True):
    uploaded_file = st.file_uploader("Выберите мем (jpg, png)", type=["jpg", "jpeg", "png"])
    name = st.text_input("Название мема")
    description = st.text_area("Описание мема")
    submitted = st.form_submit_button("Загрузить мем")

    if submitted:
        if uploaded_file is None or not name or not description:
            st.error("Пожалуйста, загрузите изображение и заполните все поля.")
        else:
            # Читаем изображение в байты
            image_bytes = uploaded_file.read()
            # Сохраняем в базу
            cursor.execute(
                "INSERT INTO memes (image, name, description, votes) VALUES (?, ?, ?, 0)",
                (image_bytes, name, description)
            )
            conn.commit()
            st.success("Мем успешно загружен!")


cursor.execute("SELECT id, image, name, description, votes FROM memes")
memes = cursor.fetchall()

if memes:
    st.header("Голосование за мемы")

    
    for meme in memes:
        meme_id, img_blob, meme_name, meme_desc, meme_votes = meme

        # Отображение изображения
        image = Image.open(io.BytesIO(img_blob))
        st.image(image, width=300)
        st.markdown(f"**{meme_name}**")
        st.markdown(f"{meme_desc}")
        st.markdown(f"Голоса: {meme_votes}")

        # Кнопка голосования
        if st.button(f"Проголосовать за '{meme_name}'", key=f"vote_{meme_id}"):
            cursor.execute("UPDATE memes SET votes = votes + 1 WHERE id = ?", (meme_id,))
            conn.commit()
            st.rerun()  
    
    cursor.execute("SELECT name, votes FROM memes ORDER BY votes DESC LIMIT 1")
    top_meme = cursor.fetchone()
    if top_meme:
        st.sidebar.header("Самый популярный мем")
        st.sidebar.write(f"**{top_meme[0]}** с {top_meme[1]} голосами")
else:
    st.info("Пока нет загруженных мемов. Будьте первым!")






