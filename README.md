# Currency Converter

**Автор:** Замятин Михаил Александрович

## Описание
Простое GUI-приложение для конвертации валют с использованием актуальных курсов из внешнего API. Сохраняет историю операций в JSON-файл.

## Как получить API-ключ
1. Перейдите на [ExchangeRate-API](https://app.exchangerate-api.com/sign-up)
2. Зарегистрируйтесь (бесплатный тариф — 1500 запросов в месяц)
3. Скопируйте ключ из личного кабинета
4. Вставьте его в код в переменную `self.api_key`

## Установка и запуск
```bash
git clone https://github.com/yourusername/currency_converter.git
cd currency_converter
pip install requests
python currency_converter.py