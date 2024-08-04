"""код создан в учебных целях для отработки навыка скраппинга"""
"""API платный"""

import requests
import fake_headers
from bs4 import BeautifulSoup
import json

"""
создать экземпляр fake_headers
browser - str, chrome/firefox/opera. User Agent browser. Default: random\n
os - str, win/mac/lin. OS of User Agent. Default: random\n
headers - bool, True/False. Generate random headers or no. Default: False
"""
headers = fake_headers.Headers(browser='chrome', os='win')

"""заходим на сайт"""
response = requests.get('https://spb.hh.ru/')

"""выгружаем html код с заголовками fake_headers"""
main_html = requests.get('https://spb.hh.ru/search/vacancy?text=python&area=1&area=2',
                        headers=headers.generate()
                        ).text

"""создать экземпляр класса, в этой переменной лежит распарсенный html код"""
main_soup = BeautifulSoup(main_html, features='lxml')

"""ищем тег со списком вакансий, первый аргумент=название тега, затем какие-либо свойства тега"""
div_vacancy_list = main_soup.find('div', id='a11y-main-content')
parsed_data = []

"""внутри тега ищем вакансии"""
tags = div_vacancy_list.find_all('div', class_='vacancy-card--z_UXteNo7bRGzxWVcL7y font-inter')

"""итерируемся по тегам; находим в древе HTML кода тег и достаем нужную информацию для будущего формирования json"""
for vacancy in tags:
    h2_tag = vacancy.find('h2')
    header = h2_tag.text.strip()
    a_tag = vacancy.find('a')
    link = a_tag['href']
    try:
        salary_tag = vacancy.find(attrs={'class':'compensation-labels--uUto71l5gcnhU2I8TZmz'})
        salary = salary_tag.text.strip()
        if '₽' in salary:
            salary = f'{salary_tag.text.strip().split("₽")[0].replace("\u202f", '')}₽'
        elif '$' in salary:
            salary = f'{salary_tag.text.strip().split("$")[0].replace("\u202f", '')}$'
        else:
            salary = 'Доход не указан'
    except:
        salary = 'error'

    company_tag = vacancy.find(attrs={'data-qa':"vacancy-serp__vacancy-employer-text"})
    try:
        name_company = company_tag.text.strip().replace("\xa0", " ")
    except AttributeError:
        continue
    city_tag = vacancy.find(attrs={'data-qa':'vacancy-serp__vacancy-address'})
    city = city_tag.text.strip()

    """отправляем запрос по каждой вакансии (ссылке), чтобы собрать информацию из описания вакансии"""
    full_vacancy_html = requests.get(
        link,
            headers=headers.generate()
    ).text
    full_vacancy_soup = BeautifulSoup(full_vacancy_html, features='lxml')

    """находим тег с начинкой вакансии"""
    full_vacancy_tag = full_vacancy_soup.find('div', class_='vacancy-description')

    """создаем пременную, включающую в себя всю инфо внутри вакансии"""
    TEXT = full_vacancy_tag.text.strip().replace("\xa0", " ")

    """Нужно выбрать те вакансии, у которых в описании есть ключевые слова Django и Flask"""
    if 'Django' in TEXT and 'Flask' in TEXT:
        parsed_data.append({
            "vacancy": header,
            "link": link,
            "salary": salary,
            "name_company": name_company,
            "city": city,
            "text": TEXT
    })
    else:
        print('Django и Flask отсутствуют в описании вакансии')

"""записываем все в json"""
for element in parsed_data:
    with open('vacancies.json', 'a') as f:
        json.dump(element, f, ensure_ascii=False, indent=2)


