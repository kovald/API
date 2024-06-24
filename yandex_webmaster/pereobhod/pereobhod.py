# импортируем необходимые библиотеки
import requests
import pandas as pd

# Замените на ваш OAuth токен
token = ""    # инструкция https://yandex.ru/dev/direct/doc/start/token.html
headers = {"Authorization": f"OAuth {token}"}

# Получить ID пользователя
user_url = "https://api.webmaster.yandex.net/v4/user"
user_response = requests.get(user_url, headers=headers)
user_id = user_response.json()["user_id"]

# Получить список хостов
hosts_url = f"https://api.webmaster.yandex.net/v4/user/{user_id}/hosts"
hosts_response = requests.get(hosts_url, headers=headers)
hosts_data = hosts_response.json()
host_ids = [host["host_id"] for host in hosts_data["hosts"]]

# Сохранить список хостов в файл "list_subdomains.txt"
with open('list_subdomains.txt', 'w') as file:
    for host_id in host_ids:
        file.write(f"{host_id}\n")

print("Список хостов успешно сохранен в файл list_subdomains.txt")

# Прочитать хосты из файла list_subdomains.txt
with open('list_subdomains.txt', 'r') as file:
    host_ids = [line.strip() for line in file.readlines()]

# Прочитать URL-адреса из текстового файла
with open('urls.txt', 'r') as file:
    urls_to_recrawl = [line.strip() for line in file.readlines()]

# Список для хранения данных
data_list = []

# Функция для форматирования host_id - приводим к виду https://site.ru
def format_host_id(host_id):
    if host_id.startswith("https:"):
        host_id = host_id.replace("https:", "https://")
    elif host_id.startswith("http:"):
        host_id = host_id.replace("http:", "http://")

    if host_id.endswith(":443"):
        host_id = host_id[:-4]

    return host_id

# Отправить на переобход страницы из файла
for host_id in host_ids:
    formatted_host_id = format_host_id(host_id)
    for page_url in urls_to_recrawl:
        # создаем полный URL
        full_page_url = f"{formatted_host_id}{page_url}" if page_url.startswith(
            '/') else f"{formatted_host_id}/{page_url}"
        recrawl_url = f"https://api.webmaster.yandex.net/v4/user/{user_id}/hosts/{host_id}/recrawl/queue"
        data = {"url": full_page_url}

        # Отправка POST запроса для переобхода
        recrawl_response = requests.post(recrawl_url, json=data, headers=headers)

        if recrawl_response.status_code == 202:
            result = recrawl_response.json()
            task_id = result["task_id"]
            quota_remainder = result["quota_remainder"]
            data_list.append({
                "host_id": host_id,
                "page_url": page_url,
                "task_id": task_id,
                "quota_remainder": quota_remainder
            })
            print(
                f"Задача {task_id} успешно создана для {formatted_host_id} и URL {page_url}. Остаток квоты: {quota_remainder}")
        else:
            print(f"Ошибка для хоста {formatted_host_id} и URL {page_url}: Статус {recrawl_response.status_code}")

# Применение форматирования и экспорт данных
if data_list:
    df = pd.DataFrame(data_list)
    df['host_id'] = df['host_id'].apply(format_host_id)  # Применение форматирования
    df.to_excel("yandex_webmaster_1.xlsx", index=False)
    print("Данные успешно экспортированы в yandex_webmaster_1.xlsx")
else:
    print("Нет данных для экспорта.")
