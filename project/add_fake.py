import requests
import json
BASEURL = 'http://127.0.0.1:8000'

# партиями по сколько человек отправлять
PARTY = 1000

with open('participants.jsonl', 'r', encoding='utf-8') as file:
    send_data = []
    for item in file.readlines():
        send_data.append(json.loads(item))
        if len(send_data) == PARTY:
            send = requests.post(f'{BASEURL}/load_fake_users', data=json.dumps(send_data))
            if send.status_code == 202:
                print(f'партия отправилась хорошо, дальше обрабатывается сервером')
                send_data = []
            else:
                print('Что то пошло не так, не отправленная партия ', send_data)
    if len(send_data) > 0:
        send = requests.post(f'{BASEURL}/load_first_users', data=json.dumps(send_data))
        if send.status_code == 202:
            print('Последняя партия отправилась хорошо')
        else:
            print('Что то пошло не так, не отправленная партия ', send_data)
