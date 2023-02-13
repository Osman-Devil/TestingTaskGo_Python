from __future__ import print_function
import os.path
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import requests
from bs4 import BeautifulSoup as BS

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 "
                  "Safari/537.36 "
}

url = f"https://confluence.hflabs.ru/pages/viewpage.action?pageId=1181220999"
r = requests.get(url)
soup = BS(r.text, "html.parser")
quotes = soup.find_all("td", class_="confluenceTd") # Поиск нужного класса и парсинга данных

# Создания двух списков
list1 = ['HTTP-код ответа']
list2 = ['Описание']
for quote in quotes:
    if quotes.index(quote) % 2 == 0:
        list1.append(quote.text)
    if quotes.index(quote) % 2 == 1:
        list2.append(quote.text)

# Подключение к GoogleSheet
class GoogleSheet:
    SPREADSHEET_ID = '1dXE8N7TDA8Xp01xmGpjeu3Rrm2hYWIZyR0PLf2-A3To' # Ip GoogleSheet
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    service = None
    
    def __init__(self):
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token: # Чтобы не запускать каждый раз авторизацию, получили токен
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                print('flow')
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('sheets', 'v4', credentials=creds)
    
    # Обновляем ячейки и значения для GoogleSheet
    def updateRangeValues(self, range, values):
        data = [{
            'range': range,
            'values': values
        }]
        body = {
            'valueInputOption': 'USER_ENTERED',
            'data': data
        }
        result = self.service.spreadsheets().values().batchUpdate(spreadsheetId=self.SPREADSHEET_ID,
                                                                  body=body).execute()
        print('{0} cells updated.'.format(result.get('totalUpdatedCells')))


def main():
    a = 0
    gs = GoogleSheet()
    test_range = 'Test!A1:B'
    test_values = []
    # Создание единого списка
    for i in list1:
        test_values.append([i, list2[a]])
        a += 1
    gs.updateRangeValues(test_range, test_values)


if __name__ == '__main__':
    main()
