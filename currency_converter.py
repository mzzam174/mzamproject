import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from datetime import datetime

class CurrencyConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Converter")
        self.root.geometry("700x500")
        self.root.resizable(False, False)

        # API ключ (бесплатный, можно получить на https://app.exchangerate-api.com/sign-up)
        self.api_key = "ВАШ_API_КЛЮЧ"  # Замените на свой ключ
        self.base_url = f"https://v6.exchangerate-api.com/v6/{self.api_key}/latest/"

        # Доступные валюты
        self.currencies = ["USD", "EUR", "UAH", "GBP", "JPY", "CAD", "AUD", "CHF", "CNY", "PLN"]

        # История
        self.history_file = "history.json"
        self.history = self.load_history()

        # Интерфейс
        self.create_widgets()
        self.update_history_table()

    def create_widgets(self):
        # Рамка для конвертации
        frame = tk.LabelFrame(self.root, text="Конвертация валют", padx=10, pady=10)
        frame.pack(padx=10, pady=10, fill="x")

        # Сумма
        tk.Label(frame, text="Сумма:").grid(row=0, column=0, sticky="w")
        self.amount_entry = tk.Entry(frame, width=15)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)

        # Из валюты
        tk.Label(frame, text="Из валюты:").grid(row=1, column=0, sticky="w")
        self.from_currency = ttk.Combobox(frame, values=self.currencies, width=10)
        self.from_currency.set("USD")
        self.from_currency.grid(row=1, column=1, padx=5, pady=5)

        # В валюту
        tk.Label(frame, text="В валюту:").grid(row=2, column=0, sticky="w")
        self.to_currency = ttk.Combobox(frame, values=self.currencies, width=10)
        self.to_currency.set("EUR")
        self.to_currency.grid(row=2, column=1, padx=5, pady=5)

        # Кнопка конвертации
        self.convert_btn = tk.Button(frame, text="Конвертировать", command=self.convert)
        self.convert_btn.grid(row=3, column=0, columnspan=2, pady=10)

        # Результат
        self.result_label = tk.Label(frame, text="Результат: --", font=("Arial", 10, "bold"))
        self.result_label.grid(row=4, column=0, columnspan=2)

        # История
        history_frame = tk.LabelFrame(self.root, text="История конвертаций", padx=10, pady=10)
        history_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Таблица истории (Treeview)
        columns = ("Дата", "Сумма", "Из", "В", "Результат")
        self.history_table = ttk.Treeview(history_frame, columns=columns, show="headings", height=12)

        for col in columns:
            self.history_table.heading(col, text=col)
            self.history_table.column(col, width=120)

        self.history_table.pack(side="left", fill="both", expand=True)

        # Скроллбар
        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_table.yview)
        scrollbar.pack(side="right", fill="y")
        self.history_table.configure(yscrollcommand=scrollbar.set)

        # Кнопка очистки истории
        clear_btn = tk.Button(self.root, text="Очистить историю", command=self.clear_history)
        clear_btn.pack(pady=5)

    def load_history(self):
        """Загружает историю из JSON-файла"""
        if os.path.exists(self.history_file):
            with open(self.history_file, "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except:
                    return []
        return []

    def save_history(self):
        """Сохраняет историю в JSON-файл"""
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=4, ensure_ascii=False)

    def update_history_table(self):
        """Обновляет отображение истории в таблице"""
        for item in self.history_table.get_children():
            self.history_table.delete(item)

        for record in self.history:
            self.history_table.insert("", "end", values=(
                record["date"],
                record["amount"],
                record["from_currency"],
                record["to_currency"],
                record["result"]
            ))

    def add_history_record(self, amount, from_curr, to_curr, result):
        """Добавляет запись в историю"""
        record = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "amount": amount,
            "from_currency": from_curr,
            "to_currency": to_curr,
            "result": result
        }
        self.history.append(record)
        # Ограничим историю 50 записями (опционально)
        if len(self.history) > 50:
            self.history.pop(0)
        self.save_history()
        self.update_history_table()

    def clear_history(self):
        """Очищает всю историю"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить всю историю?"):
            self.history = []
            self.save_history()
            self.update_history_table()
            self.result_label.config(text="Результат: --")

    def convert(self):
        """Выполняет конвертацию валюты через API"""
        # Проверка корректности ввода суммы
        amount_str = self.amount_entry.get().strip()
        if not amount_str:
            messagebox.showerror("Ошибка", "Введите сумму для конвертации")
            return

        try:
            amount = float(amount_str)
            if amount <= 0:
                messagebox.showerror("Ошибка", "Сумма должна быть положительным числом")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректный формат суммы. Введите число.")
            return

        from_curr = self.from_currency.get()
        to_curr = self.to_currency.get()

        if from_curr == to_curr:
            result = amount
            result_text = f"{amount} {from_curr} = {result:.4f} {to_curr}"
            self.result_label.config(text=f"Результат: {result:.4f}")
            self.add_history_record(amount, from_curr, to_curr, f"{result:.4f}")
            return

        # Запрос к API
        try:
            url = self.base_url + from_curr
            response = requests.get(url, timeout=10)
            data = response.json()

            if response.status_code != 200 or data.get("result") != "success":
                messagebox.showerror("Ошибка API", "Не удалось получить курс валют. Проверьте API-ключ.")
                return

            rate = data["conversion_rates"].get(to_curr)
            if not rate:
                messagebox.showerror("Ошибка", f"Валюта {to_curr} не найдена")
                return

            result = amount * rate
            result_text = f"{amount} {from_curr} = {result:.4f} {to_curr}"
            self.result_label.config(text=f"Результат: {result:.4f}")

            # Сохраняем в историю
            self.add_history_record(amount, from_curr, to_curr, f"{result:.4f}")

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Сетевая ошибка", f"Проблема с подключением: {e}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Что-то пошло не так: {e}")

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = CurrencyConverter(root)
    root.mainloop()