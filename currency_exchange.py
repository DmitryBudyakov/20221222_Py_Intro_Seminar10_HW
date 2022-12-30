import requests


def get_json_file(url, filename):
    js_data_file = requests.get(url).json()
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(js_data_file)
        
def get_json_data_from_url(url: str) -> dict:
    """ Возвращает данные в формате json """
    js_data = requests.get(url).json()
    return js_data

def get_all_currency_list(all_currency_data: dict) -> list:
    """ Возвращает список названия валют в формате /CUR """
    all_curr_dict = all_currency_data['Valute']
    all_curr_list = []
    for curr in all_curr_dict.keys():
        all_curr_list.append(f'/{curr}')
    return all_curr_list

def get_rate_for_currency(currency: str, all_curr_data: dict) -> str:
    """ Возвращает строку с курсом запрошенной валюты на актуальный Timestamp """
    currency = currency.upper()     # если введены данные не в upper регистре
    ts = all_curr_data['Timestamp'].split('T')  # ['2022-12-29', '20:00:00+03:00']
    ts_date = '-'.join(reversed(ts[0].split('-')))      # дата в виде 29-12-2022
    ts_time = ts[1]                                     # время в виде 20:00:00+03:00
    all_curr_rates = all_curr_data['Valute']    # dict с данными всех валют
    curr_data = all_curr_rates[currency]    # dict по конкретной валюте
    curr_value = \
f'Дата: {ts_date} {ts_time}\n\
{curr_data["Nominal"]} {curr_data["Name"]}\n\
{curr_data["Nominal"]} {currency} = {curr_data["Value"]} RUR'
    return curr_value
