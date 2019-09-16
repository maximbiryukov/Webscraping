import requests


def get_hh_data(query, area, pagenum):

    data = []

    output = {}

    for i in range(pagenum):

        base_url = 'http://api.hh.ru/vacancies'
        params = {'text': query, 'area': area, 'per_page': 10, 'page': i}

        request = requests.get(base_url, params=params)
        request = request.json()
        data.append(request)

    for item in data:
        temp = item['items']
        for i in temp:
            output[i['name']] = {'salary_from': i['salary'] if not i['salary'] else i['salary']['from'],
                                 'salary_to': i['salary'] if not i['salary'] else i['salary']['to'], 'url': i['url']}

    return output


a = get_hh_data('аналитик', 1, 10)
print(a)


