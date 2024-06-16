import requests
import pandas as pd

# Замените на ваш OAuth токен, инструкция https://yandex.ru/dev/direct/doc/start/token.html
token = ""
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

# Список для хранения данных
data_list = []

# Получить статистику для каждого поддомена
for host_id in host_ids:
    summary_url = f"https://api.webmaster.yandex.net/v4/user/{user_id}/hosts/{host_id}/summary"
    summary_response = requests.get(summary_url, headers=headers)
    if summary_response.status_code == 200:
        data = summary_response.json()
        formatted_host_id = f"https://{host_id.replace(':443', '').replace('https:', '')}"
        data_list.append({
            "Поддомен": formatted_host_id,
            "Проиндексированные страницы": data['searchable_pages_count'],
            "Исключенные страницы": data['excluded_pages_count'],
            "Индекс качества сайта": data['sqi'],
            "Фатальные проблемы": data['site_problems'].get('FATAL', 0),
            "Критичные проблемы": data['site_problems'].get('CRITICAL', 0),
            "Возможные проблемы": data['site_problems'].get('POSSIBLE_PROBLEM', 0),
            "Рекомендации": data['site_problems'].get('RECOMMENDATION', 0)
        })
    else:
        print(f"Ошибка для {host_id}: {summary_response.status_code}")

# Экспорт данных в файл Excel
df = pd.DataFrame(data_list)
df.to_excel("yandex_webmaster_summary.xlsx", index=False)

print("Данные успешно экспортированы в yandex_webmaster_summary.xlsx")
