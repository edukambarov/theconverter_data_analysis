import json
from pprint import pprint
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys



user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0"
edge_options = Options()
edge_options.add_argument(f'user_agent={user_agent}')
edge_options.add_argument("--disable-popup-blocking");

# Инициализация веб-драйвера
driver = webdriver.Edge(options=edge_options)

# Вспомогательная функция для очистки данных о столбцах
def clean_columns(lst: list[str]):
    for i in range(len(lst)):
        if lst[i].startswith(' '):
            lst[i-1] = lst[i-1] + lst[i]
    return lst

# Создаём список, чтобы потом положить туда словари с полученными данными и записать этот список в json
scrapped_data = []

try:
    # Открытие сайта
    driver.get("https://www.calc.ru/kalkulyator-razmerov-odezhdy.html")

    time.sleep(2)

    # Получаем список ссылок на страницы с таблицами
    raw_links = driver.find_elements(By.XPATH, '//a[contains(@class, "n12")][contains(@title,"Таблица")]')
    links = [ele.get_attribute('href') for ele in raw_links]
    time.sleep(2)
    for link in links:
        # Подключаемся к каждой странице с таблицами
        driver.get(link)
        # Создаём словарь, который положим с список scrapped_data, а позже запишем в json
        item = {'url': link}
        wait = WebDriverWait(driver, 30)
        info = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//body')))
        driver.execute_script('window.scrollTo(0, document.documentElement.scrollHeight);')
        raw_table_name = driver.find_element(By.XPATH, '//h1[contains(@itemprop, "name")]')
        item['name'] = raw_table_name.text[:-1]
        time.sleep(5)

        # Получаем список заголовков таблиц
        cols = driver.find_elements(By.XPATH,'//table[contains(@class,"razmery")]//tr[1]/td/span')
        cols = [ele.text for ele in cols]
        cols = [x for x in clean_columns(cols) if not x.startswith(' ')]
        time.sleep(5)

        # Формирование словаря, где ключ - заголовок, значение - столбец списком
        table_data = {}
        for i in range(len(cols)):
             sizes = driver.find_elements(By.XPATH,
                f'//table[contains(@class,"razmery")]//tr/td[{i}+1]')
             sizes = [x.text for x in sizes]
             table_data[cols[i]] = sizes[1:]
        item['data'] = table_data
        time.sleep(3)

        # Добавление словаря в список словарей
        scrapped_data.append(item)

        # Печать словаря в консоль
        pprint(item)
        print()


except Exception as e:
    print(f"Произошла ошибка: {e}")

finally:
    # Закрытие браузера
    driver.quit()

    # Запись файла
    with open('hw7_output_2.json', 'w', encoding='utf-8') as file:
        json.dump(scrapped_data, file, indent=4, ensure_ascii=False)








