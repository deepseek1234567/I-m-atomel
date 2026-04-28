"""
Movie Library - Личная кинотека
Автор: Илья Штыркин
Описание: GUI-приложение для хранения информации о фильмах с фильтрацией,
сохранением в JSON и валидацией ввода.
"""

import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


class MovieLibrary:
    """Основной класс приложения для управления коллекцией фильмов"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Movie Library - Личная кинотека")
        self.root.geometry("900x600")
        self.root.resizable(True, True)
        
        # Файл для хранения данных
        self.data_file = "movies.json"
        
        # Список фильмов
        self.movies = []
        
        # Загрузка сохранённых данных
        self.load_movies()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Обновление таблицы
        self.refresh_table()
    
    def create_widgets(self):
        """Создание всех элементов интерфейса"""
        
        # === Фрейм для ввода данных ===
        input_frame = tk.LabelFrame(self.root, text="Добавление фильма", padx=10, pady=10)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        # Поле Название
        tk.Label(input_frame, text="Название:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.title_entry = tk.Entry(input_frame, width=30)
        self.title_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Поле Жанр
        tk.Label(input_frame, text="Жанр:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.genre_entry = tk.Entry(input_frame, width=20)
        self.genre_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # Поле Год выпуска
        tk.Label(input_frame, text="Год выпуска:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.year_entry = tk.Entry(input_frame, width=10)
        self.year_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        # Поле Рейтинг
        tk.Label(input_frame, text="Рейтинг (0-10):").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.rating_entry = tk.Entry(input_frame, width=10)
        self.rating_entry.grid(row=1, column=3, padx=5, pady=5, sticky="w")
        
        # Кнопка добавления
        self.add_button = tk.Button(input_frame, text="➕ Добавить фильм", bg="green", fg="white",
                                    command=self.add_movie)
        self.add_button.grid(row=1, column=4, padx=10, pady=5)
        
        # === Фрейм для фильтрации ===
        filter_frame = tk.LabelFrame(self.root, text="Фильтрация", padx=10, pady=10)
        filter_frame.pack(fill="x", padx=10, pady=5)
        
        # Фильтр по жанру
        tk.Label(filter_frame, text="Фильтр по жанру:").grid(row=0, column=0, padx=5, pady=5)
        self.filter_genre_entry = tk.Entry(filter_frame, width=20)
        self.filter_genre_entry.grid(row=0, column=1, padx=5, pady=5)
        self.filter_genre_entry.bind("<KeyRelease>", self.apply_filters)
        
        # Фильтр по году
        tk.Label(filter_frame, text="Фильтр по году:").grid(row=0, column=2, padx=5, pady=5)
        self.filter_year_entry = tk.Entry(filter_frame, width=10)
        self.filter_year_entry.grid(row=0, column=3, padx=5, pady=5)
        self.filter_year_entry.bind("<KeyRelease>", self.apply_filters)
        
        # Кнопка сброса фильтров
        self.reset_button = tk.Button(filter_frame, text="🔄 Сбросить фильтры", command=self.reset_filters)
        self.reset_button.grid(row=0, column=4, padx=10, pady=5)
        
        # === Таблица для отображения фильмов ===
        table_frame = tk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Создание Treeview с прокруткой
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.tree = ttk.Treeview(table_frame, columns=("ID", "Название", "Жанр", "Год", "Рейтинг"),
                                 show="headings", yscrollcommand=scrollbar.set)
        
        # Настройка колонок
        self.tree.heading("ID", text="ID")
        self.tree.heading("Название", text="Название")
        self.tree.heading("Жанр", text="Жанр")
        self.tree.heading("Год", text="Год")
        self.tree.heading("Рейтинг", text="Рейтинг")
        
        self.tree.column("ID", width=40)
        self.tree.column("Название", width=250)
        self.tree.column("Жанр", width=150)
        self.tree.column("Год", width=80)
        self.tree.column("Рейтинг", width=80)
        
        self.tree.pack(fill="both", expand=True)
        scrollbar.config(command=self.tree.yview)
        
        # Кнопка удаления фильма
        self.delete_button = tk.Button(self.root, text="🗑 Удалить выбранный фильм", bg="red", fg="white",
                                       command=self.delete_movie)
        self.delete_button.pack(pady=5)
        
        # Статусная строка
        self.status_label = tk.Label(self.root, text="Готов к работе", bd=1, relief="sunken", anchor="w")
        self.status_label.pack(fill="x", padx=10, pady=5)
    
    def validate_movie(self, title, genre, year_str, rating_str):
        """Валидация введённых данных"""
        # Проверка названия
        if not title or not title.strip():
            return False, "Название фильма не может быть пустым!"
        
        # Проверка жанра
        if not genre or not genre.strip():
            return False, "Жанр фильма не может быть пустым!"
        
        # Проверка года
        try:
            year = int(year_str)
            current_year = datetime.now().year
            if year < 1888 or year > current_year + 5:
                return False, f"Год должен быть от 1888 до {current_year + 5}!"
        except ValueError:
            return False, "Год должен быть целым числом!"
        
        # Проверка рейтинга
        try:
            rating = float(rating_str)
            if rating < 0 or rating > 10:
                return False, "Рейтинг должен быть от 0 до 10!"
        except ValueError:
            return False, "Рейтинг должен быть числом!"
        
        return True, (title.strip(), genre.strip(), year, rating)
    
    def add_movie(self):
        """Добавление нового фильма"""
        title = self.title_entry.get()
        genre = self.genre_entry.get()
        year = self.year_entry.get()
        rating = self.rating_entry.get()
        
        # Валидация
        is_valid, result = self.validate_movie(title, genre, year, rating)
        
        if not is_valid:
            messagebox.showerror("Ошибка ввода", result)
            return
        
        title, genre, year, rating = result
        
        # Добавление фильма
        movie_id = len(self.movies) + 1
        new_movie = {
            "id": movie_id,
            "title": title,
            "genre": genre,
            "year": year,
            "rating": rating
        }
        
        self.movies.append(new_movie)
        self.save_movies()
        
        # Очистка полей
        self.title_entry.delete(0, tk.END)
        self.genre_entry.delete(0, tk.END)
        self.year_entry.delete(0, tk.END)
        self.rating_entry.delete(0, tk.END)
        
        # Обновление таблицы
        self.refresh_table()
        self.status_label.config(text=f"Фильм '{title}' успешно добавлен!")
    
    def delete_movie(self):
        """Удаление выбранного фильма"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите фильм для удаления!")
            return
        
        # Получение ID выбранного фильма
        item = self.tree.item(selected[0])
        movie_id = int(item['values'][0])
        
        # Подтверждение удаления
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этот фильм?"):
            # Удаление фильма
            self.movies = [m for m in self.movies if m['id'] != movie_id]
            
            # Перенумерация ID
            for i, movie in enumerate(self.movies, 1):
                movie['id'] = i
            
            self.save_movies()
            self.refresh_table()
            self.status_label.config(text="Фильм успешно удалён!")
    
    def apply_filters(self, event=None):
        """Применение фильтров"""
        genre_filter = self.filter_genre_entry.get().strip().lower()
        year_filter = self.filter_year_entry.get().strip()
        
        filtered_movies = self.movies.copy()
        
        # Фильтр по жанру
        if genre_filter:
            filtered_movies = [m for m in filtered_movies if genre_filter in m['genre'].lower()]
        
        # Фильтр по году
        if year_filter:
            try:
                year_int = int(year_filter)
                filtered_movies = [m for m in filtered_movies if m['year'] == year_int]
            except ValueError:
                pass
        
        self.update_table(filtered_movies)
        
        count = len(filtered_movies)
        self.status_label.config(text=f"Найдено фильмов: {count}")
    
    def reset_filters(self):
        """Сброс всех фильтров"""
        self.filter_genre_entry.delete(0, tk.END)
        self.filter_year_entry.delete(0, tk.END)
        self.refresh_table()
        self.status_label.config(text="Фильтры сброшены")
    
    def refresh_table(self):
        """Обновление таблицы с учётом фильтров"""
        self.apply_filters()
    
    def update_table(self, movies_list):
        """Обновление отображаемых данных в таблице"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Заполнение таблицы
        for movie in movies_list:
            self.tree.insert("", "end", values=(
                movie['id'],
                movie['title'],
                movie['genre'],
                movie['year'],
                f"{movie['rating']:.1f}" if isinstance(movie['rating'], float) else str(movie['rating'])
            ))
    
    def save_movies(self):
        """Сохранение данных в JSON файл"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.movies, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")
    
    def load_movies(self):
        """Загрузка данных из JSON файла"""
        if not os.path.exists(self.data_file):
            # Пример данных для демонстрации
            self.movies = [
                {"id": 1, "title": "Побег из Шоушенка", "genre": "Драма", "year": 1994, "rating": 9.3},
                {"id": 2, "title": "Крёстный отец", "genre": "Криминал", "year": 1972, "rating": 9.2},
                {"id": 3, "title": "Тёмный рыцарь", "genre": "Боевик", "year": 2008, "rating": 9.0}
            ]
            self.save_movies()
            return
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.movies = json.load(f)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")
            self.movies = []


def run_tests():
    """Функция для тестирования (вызывается отдельно)"""
    print("=" * 50)
    print("Запуск тестирования Movie Library")
    print("=" * 50)
    
    # Создание экземпляра для тестирования (без GUI)
    class MockMovieLibrary:
        def __init__(self):
            self.movies = []
        
        def validate_movie(self, title, genre, year_str, rating_str):
            """Копия метода валидации для тестирования"""
            if not title or not title.strip():
                return False, "Название фильма не может быть пустым!"
            if not genre or not genre.strip():
                return False, "Жанр фильма не может быть пустым!"
            try:
                year = int(year_str)
                from datetime import datetime
                current_year = datetime.now().year
                if year < 1888 or year > current_year + 5:
                    return False, f"Год должен быть от 1888 до {current_year + 5}!"
            except ValueError:
                return False, "Год должен быть целым числом!"
            try:
                rating = float(rating_str)
                if rating < 0 or rating > 10:
                    return False, "Рейтинг должен быть от 0 до 10!"
            except ValueError:
                return False, "Рейтинг должен быть числом!"
            return True, (title.strip(), genre.strip(), year, rating)
    
    test_app = MockMovieLibrary()
    tests_passed = 0
    tests_total = 0
    
    # Позитивные тесты
    print("\n--- Позитивные тесты ---")
    test_cases = [
        ("Интерстеллар", "Фантастика", "2014", "8.6", True),
        ("1+1", "Драма", "2011", "8.5", True),
        ("Отель "Гранд Будапешт"", "Комедия", "2014", "8.1", True),
    ]
    
    for title, genre, year, rating, expected in test_cases:
        tests_total += 1
        result, _ = test_app.validate_movie(title, genre, year, rating)
        if result == expected:
            tests_passed += 1
            print(f"✓ PASS: {title}")
        else:
            print(f"✗ FAIL: {title}")
    
    # Негативные тесты
    print("\n--- Негативные тесты ---")
    neg_tests = [
        ("", "Драма", "2020", "7.5", False, "Пустое название"),
        ("Фильм", "", "2020", "7.5", False, "Пустой жанр"),
        ("Фильм", "Драма", "abcd", "7.5", False, "Год не число"),
        ("Фильм", "Драма", "2020", "15", False, "Рейтинг > 10"),
        ("Фильм", "Драма", "2020", "-1", False, "Рейтинг < 0"),
        ("Фильм", "Драма", "1800", "7.5", False, "Год < 1888"),
    ]
    
    for title, genre, year, rating, expected, desc in neg_tests:
        tests_total += 1
        result, _ = test_app.validate_movie(title, genre, year, rating)
        if result == expected:
            tests_passed += 1
            print(f"✓ PASS: {desc}")
        else:
            print(f"✗ FAIL: {desc}")
    
    # Граничные тесты
    print("\n--- Граничные тесты ---")
    boundary_tests = [
        ("Фильм", "Драма", "1888", "0", True, "Минимальный год + минимальный рейтинг"),
        ("Фильм", "Драма", "2025", "10", True, "Максимальный год + максимальный рейтинг"),
    ]
    
    for title, genre, year, rating, expected, desc in boundary_tests:
        tests_total += 1
        result, _ = test_app.validate_movie(title, genre, year, rating)
        if result == expected:
            tests_passed += 1
            print(f"✓ PASS: {desc}")
        else:
            print(f"✗ FAIL: {desc}")
    
    print("\n" + "=" * 50)
    print(f"Результаты тестирования: {tests_passed}/{tests_total} пройдено")
    print(f"Процент успешных тестов: {tests_passed/tests_total*100:.1f}%")
    print("=" * 50)
    
    return tests_passed, tests_total


if __name__ == "__main__":
    import sys
    
    # Проверка аргументов командной строки для запуска тестов
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
    else:
        root = tk.Tk()
        app = MovieLibrary(root)
        root.mainloop()