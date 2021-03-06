import os
import csv
import math
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


def scrap_one_product(home: str, url: str, category: str, ratings: list) -> list:
    """Récupération des infos d'un produit via url"""
    data = {}
    page = requests.get(home + url)
    soup = BeautifulSoup(page.content, 'html.parser')

    table = soup.find('table', class_='table-striped')
    tds = table.find_all('td')

    data['product_page_url'] = home + url
    data['upc'] = tds[0].string
    title = soup.find('div', class_='product_main').find('h1').string
    data['title'] = title
    data['price_incl_tax'] = tds[2].string
    data['price_excl_tax'] = tds[3].string
    number = re.findall(r"\d+", tds[5].string)
    data['number_available'] = number[0]
    try:
        data['product_description'] = soup.find(id='product_description').find_next('p').string
    except:
        data['product_description'] = ''
        # logger si pas de description
    data['category'] = category
    data['review_rating'] = ratings[soup.find('p', class_='star-rating').attrs['class'][1]]
    data['image_url'] = home + soup.find(id='product_gallery').find('img').attrs['src'].replace('../../', '/')

    return data


def save_to_csv(csv_header: list, data: list, category: str):
    categories_path = os.path.curdir + '/extraction/csv/'
    if not os.path.isdir(categories_path):
        os.mkdir(categories_path)
    csv_path = categories_path + category + '.csv'

    with open(csv_path, 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow(csv_header)
        for d in data:
            writer.writerow(d)


def get_categories(home_url: str) -> dict:
    categories = {}
    page = requests.get(home_url)
    if page.status_code != 200:
        print(f"Impossible de se connecter à {home_url}") 
    soup = BeautifulSoup(page.content, 'html.parser')
    side_categories = soup.find('div', class_='side_categories').find_all('a')
    for side_cat in side_categories:
        cat_name = side_cat.string.strip()
        if cat_name != 'Books':
            categories[cat_name] = side_cat.attrs['href'].strip()

    return categories


def get_books_by_category(category_url: str) -> dict:
    books = {}
    page = requests.get(category_url)
    if page.status_code != 200:
        print("La page demandée n'a pas pu être atteinte")
    soup = BeautifulSoup(page.content, 'html.parser')
    number_of_products = int(soup.find('form', class_='form-horizontal').find_all('strong')[0].string)
    number_of_pages = math.ceil(number_of_products / 20)

    books.update(get_books_by_page(category_url))

    if number_of_pages > 1:
        next_page = 2
        while next_page <= number_of_pages:
            page_url = category_url.replace('index', 'page-' + str(next_page))
            books.update(get_books_by_page(page_url))
            next_page += 1

    return books


def get_books_by_page(page_url: str) -> dict:
    books = {}
    page = requests.get(page_url)
    if page.status_code != 200:
        print("La page demandée n'a pas pu être atteinte")
    soup = BeautifulSoup(page.content, 'html.parser')
    products = soup.find_all('article', class_='product_pod')
    for product in products:
        partial_url = product.find('a').attrs['href'].replace('../../../', '/catalogue/')
        title = product.find('img').attrs['alt']
        books[partial_url] = title

    return books


def download_image(url: str, path:str, file_name: str):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        extension = os.path.splitext(url)[1]
        os.makedirs(path, exist_ok=True)
        file_name = path + '/' + file_name + extension
        with open(file_name, 'wb') as file:
            shutil.copyfileobj(response.raw, file)
    else:
        print("\t\t\tERREUR : L'image n'a pas pu être téléchargée.")


def main():
    categories = get_categories(HOME)
    for cat_name, cat_url in categories.items():
        print('\n' + cat_name.upper())
        all_data = []
        book_number = 1
        working_url = HOME + '/' + cat_url

        books = get_books_by_category(working_url)
        for url, title in books.items():
            print(f"\t[#{str(book_number)}] {title}")

            page = requests.get(working_url)
            if page.status_code != 200:
                print(f"Impossible de se connecter à {working_url}")
                break
            one_data = scrap_one_product(HOME, url, cat_name, RATINGS)
            values = list(one_data.values())
            all_data.append(values)
            download_image(values[-1], 'extraction/images/' + cat_name, values[1])
            book_number += 1

        save_to_csv(list(one_data.keys()), all_data, cat_name)


if __name__ == "__main__":
    main()
