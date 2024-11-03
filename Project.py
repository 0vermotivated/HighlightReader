# импорт библиотек
import tkinter as tk
from tkinter import filedialog, colorchooser

# заголовок приложения
APP_TITLE = "Проект"
# количество символов на одной странице,
# лучше было по словам, но у меня не робило
PAGE_SIZE = 1300
dark_mode = False # темная тема
text_content = ""  # весь текст из файла
current_page = 0  # страница
animation_color = "#ff0000"  # цвет анимации
words = []  # список слов для анимации
animation_running = False  # флаг воспроизведения анимации
animation_speed = 100  # начальная скорость


# Загрузка текста из файла и деление его на страницы
def load_text():
    # подтягиваем переменные снаружи
    global text_content, current_page, words
    # запрашиваем файл
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if not file_path:
        return  # если файл не выбран, просто выходим из функции
    # txt файлы могут иметь разную кодировку, из-за чего все может слетать
    # тут идет перебор 3-х основных кодировок
    for encoding in ["utf-8", "cp1251", "iso-8859-1"]:
        try:
            with open(file_path, "r", encoding=encoding) as file:
                text_content = file.read()
            break  # если удалось прочитать, выходим из цикла
        except UnicodeDecodeError:
            continue  # пробуем следующую кодировку
    # устанавливаем первую страницу после загрузки текста
    current_page = 0
    display_page()


# функция для отображения текущей страницы
def display_page():
    global current_page, words
    # очищаем текстовое поле перед отображением новой страницы
    text_widget.delete(1.0, tk.END)
    # вычисляем начало и конец страницы
    start_index = current_page * PAGE_SIZE
    end_index = start_index + PAGE_SIZE
    # выбираем текст для текущей страницы и вставляем его в текстовое поле
    page_text = text_content[start_index:end_index]
    text_widget.insert(tk.END, page_text)
    # обновляем отображение номера страницы
    page_label.config(text=f"Страница {current_page + 1} из {get_total_pages()}")
    # обновляем список слов для анимации
    words = page_text.split()


# кол-во страниц
def get_total_pages():
    return (len(text_content) + PAGE_SIZE - 1) // PAGE_SIZE


# переход на следующую страницу
def next_page():
    global current_page
    if current_page < get_total_pages() - 1:
        current_page += 1
        display_page()


# переход на предыдущую страницу
def previous_page():
    global current_page
    if current_page > 0:
        current_page -= 1
        display_page()


# триггер старт анимация
def start_word_animation():
    global animation_running
    animation_running = True    # ставим флаг
    animate_background_by_words(0)  # начинаем анимацию с первого слова на странице

# остановка анимации
def stop_word_animation():
    global animation_running
    animation_running = False
    text_widget.tag_remove("animate_bg", "1.0", tk.END)  # убираем все подсветки

# закрашивание фона
def animate_background_by_words(index, start_pos="1.0"):
    global words, animation_running
    if not animation_running:  # проверка флага
        return

    if index >= len(words):
        # если достигли конца страницы, переходим на следующую
        if current_page < get_total_pages() - 1:
            next_page()  # переход на следующую страницу
            # начинаем анимацию с первого слова на новой странице
            index = 0
            words = text_widget.get(1.0, tk.END).split()  # обновляем слова на новой странице
            start_pos = "1.0"  # сброс начальной позиции

    if index < len(words):
        # убираем предыдущую анимацию, если есть
        text_widget.tag_remove("animate_bg", "1.0", tk.END)

        # получаем текущее слово и ищем его после start_pos
        word = words[index]
        start_index = text_widget.search(word, start_pos, stopindex=tk.END)

        if start_index:
            # устанавливаем индекс конца тега
            end_index = f"{start_index} + {len(word)} chars"
            # закрашиваем фон текущего слова
            text_widget.tag_add("animate_bg", start_index, end_index)
            text_widget.tag_config("animate_bg", background=animation_color)

            # через 500 мс снимаем тег анимации, но работает это иначе
            # честно, хз почему
            root.after(500, lambda: text_widget.tag_remove("animate_bg", start_index, end_index))

            # обновляем стартовую позицию для следующего поиска
            next_start_pos = end_index
        # переходим к следующему слову с задержкой
        root.after(600 - animation_speed, animate_background_by_words, index + 1, next_start_pos)


# функция для выбора цвета подсветки
def choose_color():
    global animation_color
    color = colorchooser.askcolor(title="Выберите цвет подсветки")
    if color[1]:
        animation_color = color[1]
        text_widget.tag_config("animate_bg", background=animation_color)


# установка скорости анимации
def set_speed(speed):
    global animation_speed
    animation_speed = speed


def toggle_dark_mode():
    global dark_mode
    dark_mode = not dark_mode   # свитч флага даркмода
    # цвета областей, если флаг тру - левый, фолс - правый
    bg_color = "#333333" if dark_mode else "white"
    fg_color = "white" if dark_mode else "black"
    button_bg = "#555555" if dark_mode else "lightgray"
    slider_bg = "#444444" if dark_mode else "white"
    # обновление цветов в окне
    root.configure(bg=bg_color)
    text_widget.configure(bg=bg_color, fg=fg_color, insertbackground=fg_color)
    button_frame.configure(bg=bg_color)
    # обновляем все кнопки и метки
    for widget in button_frame.winfo_children():
        if isinstance(widget, tk.Button):
            widget.configure(bg=button_bg, fg=fg_color)
        elif isinstance(widget, tk.Label):
            widget.configure(bg=bg_color, fg=fg_color)
    # цвет слайдера отдельно
    speed_scale.configure(bg=bg_color, fg=fg_color, troughcolor=slider_bg, highlightbackground=bg_color)

# выход
def exit_application():
    root.destroy()


# создаем окно
root = tk.Tk()
root.title(APP_TITLE)
root.geometry("1100x700")  # размер окна
# создаем текстовое поле с размерами меньше, чем окно приложения
text_widget = tk.Text(root, wrap=tk.WORD, font=("Helvetica", 14), bg="white", height=25, width=80)
text_widget.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)  # добавляем отступы
# фрейм кнопок
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

# КНОПКИ
load_button = tk.Button(button_frame, text="Загрузить текст из файла", command=load_text)
load_button.pack(side=tk.LEFT, padx=5)
prev_button = tk.Button(button_frame, text="Назад", command=previous_page)
prev_button.pack(side=tk.LEFT, padx=5)
page_label = tk.Label(button_frame, text="Страница 1 из 1")
page_label.pack(side=tk.LEFT, padx=5)
next_button = tk.Button(button_frame, text="Вперед", command=next_page)
next_button.pack(side=tk.LEFT, padx=5)
animate_button_words = tk.Button(button_frame, text="Анимация по словам", command=start_word_animation)
animate_button_words.pack(side=tk.LEFT, padx=5)
stop_button = tk.Button(button_frame, text="Остановить анимацию", command=stop_word_animation)
stop_button.pack(side=tk.LEFT, padx=5)
color_button = tk.Button(button_frame, text="Выбрать цвет подсветки", command=choose_color)
color_button.pack(side=tk.LEFT, padx=5)
speed_scale = tk.Scale(button_frame, from_=50, to=500, label="Скорость", orient=tk.HORIZONTAL, command=lambda value: set_speed(int(value)))
speed_scale.set(animation_speed)  # нач скорость
speed_scale.pack(side=tk.LEFT, padx=5)
dark_mode_button = tk.Button(button_frame, text="Темная тема", command=toggle_dark_mode)
dark_mode_button.pack(side=tk.LEFT, padx=5)
exit_button = tk.Button(button_frame, text="Выход", command=exit_application)
exit_button.pack(side=tk.LEFT, padx=1)
# тег для анимации
text_widget.tag_configure("animate_bg", background=animation_color)

# запуск
root.mainloop()
