import httplib2 
from googleapiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials
import os, json


def table(email, settings):
    CREDENTIALS_FILE = 'keys.json'

    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'])

    httpAuth = credentials.authorize(httplib2.Http())
    service = discovery.build('sheets', 'v4', http = httpAuth)

    driveService = discovery.build('drive', 'v3', http=httpAuth)

    spreadsheet = service.spreadsheets().create(body = {
        'properties': {'title': settings['title'], 'locale': 'ru_RU'},
        'sheets': [{'properties': {'sheetType': 'GRID',
                                   'sheetId': 0,
                                   'title': settings['sheetName'],
                                   'gridProperties': {'rowCount': 100, 'columnCount': 15}}}]
    }).execute()



    spreadsheetId = spreadsheet['spreadsheetId']

    access = driveService.permissions().create(
        fileId = spreadsheetId,
        body = {'type': 'user', 'role': 'writer', 'emailAddress': f'{email}'},
        fields = 'id'
    ).execute()

    if os.path.exists('access.json'):
        with open('access.json', 'r') as f:
            loaded = json.load(f)
        loaded[settings['nameForRowJSON']] = {'spreadsheetId': spreadsheetId,
                                               'sheet': settings['sheetName']}
    else:
        loaded = {settings['nameForRowJSON']: {'spreadsheetId': spreadsheetId,
                                               'sheet': settings['sheetName']}}

    with open('access.json', 'w') as f:
        json.dump(loaded, f)

    print('https://docs.google.com/spreadsheets/d/' + spreadsheetId)


def change(settings):
    CREDENTIALS_FILE = 'keys.json'
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'])
    httpAuth = credentials.authorize(httplib2.Http())
    service = discovery.build('sheets', 'v4', http = httpAuth)
    with open('access.json') as f:
        data = json.load(f)
    spreadsheetId = data[settings[0]]['spreadsheetId']
    changing = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheetId,
                                                           body = {
                                                            'valueInputOption': 'USER_ENTERED',
                                                            'data': [
                                                                {
                                                                    'range': f'{data[settings[0]]["sheet"]}!{settings[1]}',
                                                                    'majorDimension': 'ROWS',
                                                                    'values': [
                                                                        [f'{settings[2]}'],
                                                                    ]
                                                                }
                                                            ]
                                                           }
                                                           ).execute()
    print('Done!')


def set_access(email, settings):
    CREDENTIALS_FILE = 'keys.json'
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'])
    httpAuth = credentials.authorize(httplib2.Http())
    service = discovery.build('sheets', 'v4', http = httpAuth)
    with open('access.json') as f:
        data = json.load(f)
    spreadsheetId = data[settings[0]]['spreadsheetId']
    driveService = discovery.build('drive', 'v3', http=httpAuth)
    access = driveService.permissions().create(
        fileId = spreadsheetId,
        body = {'type': 'user', 'role': 'writer', 'emailAddress': f'{email}'},
        fields = 'id'
    ).execute()
    print('Доступ предоставлен')


def link_for_table(title):
    with open('access.json', 'r') as f:
        data = json.load(f)
    if title in data.keys():
        return 'https://docs.google.com/spreadsheets/d/' + data[title]['spreadsheetId']
    else:
        return 'Таблицы с таким названием нет('


if __name__ == '__main__':
    # create_table({'title': 'myDoc', 'sheetName': 'sheet1', 'nameForRowJSON': 'myDoc'})
    set_access('esenianazarenkova4159@gmail.com', ['myDoc'])
    change(['myDoc', 'B2', 'Я поменял ячейку'])