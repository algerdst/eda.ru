import json
import os
import random
import time
import logging
import cloudscraper
from bs4 import BeautifulSoup
import datetime
from fake_useragent import UserAgent

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Инициализация UserAgent
ua = UserAgent()

# Создание сессии CloudScraper
scraper = cloudscraper.create_scraper()

def set_random_user_agent():
    """ Устанавливает случайный User Agent для сессии scraper. """
    random_user_agent = ua.random
    scraper.headers.update({'User-Agent': random_user_agent})

# Создание директории для сохранения JSON файлов, если она еще не существует
if not os.path.exists('eda'):
    os.makedirs('eda')

def parse(urls):
    # Создание файла для записи URL с ошибками, если он не существует
    if not os.path.exists('fail_url.txt'):
        with open('fail_url.txt', 'w') as f:
            pass

    with open(urls, 'r', encoding='utf-8') as file:
        count=1
        for url in file:
            try:
                set_random_user_agent()  # Смена User Agent перед каждым запросом
                url = url.strip()
                response = scraper.get(url)
                response.raise_for_status()  # Проверка на ошибки HTTP
                soup = BeautifulSoup(response.text, 'lxml')
                url=url.replace('\n','')
                response=scraper.get(url)
                soup=BeautifulSoup(response.text,'lxml')
                title=soup.find('h1').text.replace(' ',' ')
                li_breadcrumbs=soup.find('nav').findAll('li')
                breadcrumbs=''
                for li in li_breadcrumbs:
                    breadcrumbs+=li.text+'>'
                breadcrumbs=breadcrumbs.strip('>')
                cooking_time=soup.find('div',class_='emotion-my9yfq').text
                energy_value=soup.findAll('div', class_='emotion-8fp9e2')
                calories=energy_value[0].text+' '+'ккал'
                protein=energy_value[1].text+' '+'грамм'
                fat=energy_value[2].text+' '+'грамм'
                carb=energy_value[3].text+' '+'грамм'
                ingrs_blocks=soup.findAll('div', class_='emotion-7yevpr')
                ingredients=''
                for i in ingrs_blocks:
                    ingredient=''
                    item=i.find('span', class_='emotion-mdupit').text
                    weight=i.find('span', class_='emotion-bsdd3p').text
                    ingredient+=item+' '+weight
                    ingredients+=ingredient+'\n'
                total_steps=''
                steps_blocks=soup.findAll('div', class_='emotion-19fjypw')
                if not steps_blocks:
                    steps_blocks=soup.findAll('div', class_='emotion-ip3ree')
                for step in steps_blocks:
                    number=step.findAll('span')[0].text
                    step_descr=step.findAll('span')[1].text
                    step=number+' '+step_descr
                    total_steps+=step+'\n'
                total_steps=total_steps.replace(' ',' ')
                now=str(datetime.datetime.now())[:19]
                result_json={
                    'Название блюда': title,
                    'Время приготовления': cooking_time,
                    'Ингредиенты': ingredients,
                    'Пошаговый рецепт': total_steps,
                    'Хлебные крошки': breadcrumbs,
                    'Калорийность на порцию': calories,
                    'Содержание белка на порцию': protein,
                    'Содержание жира на порцию': fat,
                    'Содержание углеводов на порцию': carb,
                    'url':url
                }
                path=f"{title} {now}.json".replace(':','-').replace('"','')
                path=str(path)
                with open(f"eda/{path}", 'w', encoding='utf-8-sig') as file:
                    json.dump(result_json,file, indent=4, ensure_ascii=False)
                time.sleep(random.randint(1,2))
                logging.info(f"Собрано {count} рецептов")
                count+=1
            except Exception as ex:
                logging.error(f"Ошибка при обработке URL {url}: {ex}")
                with open('fail_url.txt', 'a') as fail_file:
                    fail_file.write(url + '\n')

parse('links.txt')