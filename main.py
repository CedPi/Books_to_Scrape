import os
import csv
import re
import requests
import shutil
from bs4 import BeautifulSoup


HOME = 'http://books.toscrape.com'

RATINGS = {
    'One': 1,
    'Two': 2,
    'Three': 3,
    'Four': 4,
    'Five': 5
}

HEADER = [
    'product_page_url',
    'universal_product_code (upc)',
    'title',
    'price_including_tax',
    'price_excluding_tax',
    'number_available',
    'product_description',
    'category',
    'review_rating',
    'image_url'
]


def scrap_one_product(home: str, url: str, category: str, ratings: list) -> list:
    """Récupération des infos d'un produit via url"""
    data = []
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    table = soup.find('table', class_='table-striped')
    tds = table.find_all('td')

    # product page url
    data.append(url)
    # upc
    data.append(tds[0].string)
    # title
    title = soup.find('div', class_='product_main').find('h1').string
    data.append(title)
    print('\t\t' + title)
    # price including tax
    data.append(tds[2].string)
    # price excluding tax
    data.append(tds[3].string)
    # number available
    number = re.findall(r"\d+", tds[5].string)
    data.append(number[0])
    # product description
    try:
        data.append(soup.find(id='product_description').find_next('p').string)
    except:
        data.append('')
        print("\t\t\t(No description found for : " + title + ')')
    # category
    data.append(category)
    # review rating
    data.append(ratings[soup.find('p', class_='star-rating').attrs['class'][1]])
    # image url
    data.append(home + soup.find(id='product_gallery').find('img').attrs['src'].replace('../../', '/'))

    return data


def save_to_csv(csv_header: list, data: list, category: str):
    categories_path = os.path.curdir + '/categories'
    if not os.path.isdir(categories_path):
        os.mkdir('categories')
    csv_path = 'categories/' + category + '.csv'

    with open(csv_path, 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow(csv_header)
        for d in data:
            writer.writerow(d)


def get_categories(home_url: str) -> list:
    categories = dict()
    page = requests.get(home_url)
    soup = BeautifulSoup(page.content, 'html.parser')
    side_categories = soup.find('div', class_='side_categories').find_all('a')
    for side_cat in side_categories:
        cat_name = side_cat.string.strip()
        if cat_name != 'Books':
            categories[cat_name] = side_cat.attrs['href'].strip()
    return categories


def download_image(url: str, path:str, file_name: str):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        extension = os.path.splitext(url)[1]
        os.makedirs(path, exist_ok=True)
        file_name = path + '/' + file_name + extension
        with open(file_name, 'wb') as file:
            shutil.copyfileobj(response.raw, file)
        print("\t\t\t>>> L'image a bien été téléchargée")
    else:
        print("\t\t\tERREUR : L'image n'a pas pu être téléchargée.")



# Main program
categories = get_categories(HOME)
for cat_name, cat_url in categories.items():
    print('\n' + cat_name.upper())
    all_data = []
    page_number = 1
    cat_url_wo_index = cat_url.replace('/index.html', '')
    working_url = HOME + '/' + cat_url

    while True:
        page = requests.get(working_url)
        if page.status_code != 200:
            break

        print('\t[ Page ' + str(page_number) + ' : ' + working_url + ' ]')
        soup = BeautifulSoup(page.content, 'html.parser')
        number_of_products = int(soup.find('form', class_='form-horizontal').find_all('strong')[0].string)
        products = soup.find_all('article', class_='product_pod')
        
        for product in products:
            product_url = HOME + product.find('a').attrs['href'].replace('../../../', '/catalogue/')
            one_data = scrap_one_product(HOME, product_url, cat_name, RATINGS)
            all_data.append(one_data)
            download_image(one_data[-1], 'images/' + cat_name, one_data[1])

        if number_of_products > 20:
            page_number += 1
            working_url = HOME + '/' + cat_url_wo_index + '/page-' + str(page_number) + '.html'
        else:
            break

    save_to_csv(HEADER, all_data, cat_name)
