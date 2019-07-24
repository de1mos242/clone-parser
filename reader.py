import json
import re

import bs4
import requests


def parse_main(data, root_url):
    root = bs4.BeautifulSoup(data, 'html5lib')
    result = {}
    table: bs4.Tag = root.find('tbody')
    for row in table.find_all('tr'):
        row: bs4.Tag = row
        values = row.find_all('td')
        result[row.find('th').text] = {
            'link': root_url + values[0].find('a').attrs['href'],
            'img': root_url + values[0].find('img').attrs['src'],
            'name': values[1].text,
            'color': values[2].text,
            'element': values[3].text,
            'type': values[4].text
        }
    print(json.dumps(result))
    return result


def read_main(url):
    response = requests.get(url)
    data = response.text
    return data


def enchance_data(item):
    soup = bs4.BeautifulSoup(requests.get(item['link']).text, 'html5lib')
    rows = soup.find_all('div', class_='row')
    requirement_cards = rows[1].find_all('div', class_='card')[:-1] + rows[2].find_all('div', class_='card')[:-2]
    depends_on_ids = [re.findall(r'/(\d+)$', card.find('a').attrs['href'])[0]
                      for card in requirement_cards
                      if card.find('a') is not None]
    item['depends_on'] = depends_on_ids
    makes_tag = rows[4].find('a')
    item['makes'] = re.findall(r'/(\d+)$', makes_tag.attrs['href'])[0] if makes_tag else None


def main():
    root_url = 'https://clone-evolution.ru'
    main_text = read_main(root_url + '/cloneevo/')
    # root = parse_main(main_text, root_url)

    with open('main_data.json') as f:
        root = json.load(f)
    print(root)

    for item in root.values():
        enchance_data(item)
    print(root)
    print(json.dumps(root))


def get_group_by_color(color):
    map = {
        'Серый': 1,
        'Зеленый': 2,
        'Синий': 3,
        'Фиолетовый': 4,
        'Золотой': 5,
        'Красный': 6
    }
    return map[color]

def main2():
    with open('full_data.json') as f:
        root = json.load(f)
    print(root)
    nodes = [dict(id=k, img=v['img'], name=v['name'], group=get_group_by_color(v['color'])) for k, v in root.items()]
    links = [dict(source=k, target=v['depends_on']) for k, v in root.items() if v['depends_on']]
    real_links = []
    for l in links:
        for target in l['target']:
            real_links.append(dict(source=l['source'], target=target, value=1))
    print(json.dumps(dict(nodes=nodes, links=real_links)))

if __name__ == '__main__':
    main2()
