import csv
import requests

# Замените на ваш OAuth токен
token = ""

headers = {"Authorization": f"OAuth {token}"}

# Telegram Bot конфигурация
telegram_bot_token = "ваш_токен_бота"
telegram_chat_id = "ваш_chat_id"

# Получить ID пользователя
user_url = "https://api.webmaster.yandex.net/v4/user"
user_response = requests.get(user_url, headers=headers)
user_id = user_response.json()["user_id"]

# Конфигурация
API_URL = f"https://api.webmaster.yandex.net/v4/user/{user_id}/hosts/{{host_id}}/recrawl/queue/"
HOST_ID = "ваш_host_id"  # Замените на ваш HOST_ID
LIMIT = 10  # Количество URL, обрабатываемых за один запуск скрипта

def read_urls(file_path):
    """
    Читает URL из файла CSV и возвращает их в виде списка.
    """
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        urls = [row[0] for row in reader]
    return urls

def write_urls(file_path, urls):
    """
    Записывает список URL в файл CSV, перезаписывая существующие данные.
    """
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for url in urls:
            writer.writerow([url])

def send_url_to_recrawl(url):
    """
    Отправляет URL на переобход в Яндекс Вебмастер.
    Возвращает True, если запрос был успешным, иначе False.
    """
    headers = {
        "Authorization": f"OAuth {token}",
        "Content-Type": "application/json"
    }
    data = {
        "url": url
    }
    response = requests.post(API_URL.format(host_id=HOST_ID), json=data, headers=headers)
    return response.status_code == 200

def send_telegram_message(message):
    """
    Отправляет сообщение в Telegram с использованием Bot API.
    """
    send_text = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage?chat_id={telegram_chat_id}&text={message}"
    response = requests.get(send_text)
    return response.json()

def main():
    """
    Основная функция, выполняющая следующие действия:
    1. Чтение URL из файла urls.csv.
    2. Проверка на пустой список URL. Если пуст, отправка сообщения в Telegram.
    3. Отправка URL на переобход в Яндекс Вебмастер, ограничивая количество до значения LIMIT.
    4. Обновление файла urls.csv с оставшимися URL.
    """
    urls = read_urls('urls.csv')
    if not urls:
        # Если список URL пуст, отправляем сообщение в Telegram и завершаем выполнение.
        send_telegram_message(f"Все URL {HOST_ID} обработаны.")
        return

    for _ in range(min(LIMIT, len(urls))):
        url = urls.pop(0)  # Берем первый URL из списка и удаляем его
        send_url_to_recrawl(url)  # Отправляем URL на переобход

    # Перезаписываем файл urls.csv оставшимися URL
    write_urls('urls.csv', urls)

if __name__ == "__main__":
    main()  # Запуск основной функции
