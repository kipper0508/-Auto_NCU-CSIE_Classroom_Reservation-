import requests
import argparse
import json
import os
from lxml import html
import datetime

parser = argparse.ArgumentParser('python3 clock.py')
parser.add_argument("--config", default="config.json", help="default: %(default)s")
parser.add_argument("-c", "--classroom", default="default_room", help="classrooms are defined in config.json. default: %(default)s ")
args = parser.parse_args()

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

week = {"Monday":0,"Tuesday":1,"Wednesday":2,"Thursday":3,"Friday":4,"Saturday":5,"Sunday":6}

def main():
    with open(args.config,encoding='utf-8-sig') as config_file:
        config = json.load(config_file)

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'Host': 'portal.ncu.edu.tw',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
    }

    session = requests.session()

    login(session, headers, config['account'], config['password'])
    
    if(len(config["rooms"][args.classroom]['date'])>1 and "EVERY" in config["rooms"][args.classroom]['date'] ):
        print("Warning: Do not use EVERY tag with target day mode")

    if(sign(session, config["rooms"][args.classroom])):
        print("Sucess")
    else:
        print("Error!")
    

def login(session, headers, account, password):
    payload = {
        'language' : 'CHINESE',
        'username' : account,
        'password' : password
    }

    r = session.get('https://portal.ncu.edu.tw/login', headers=headers)

    # Get CSRF token from portal login page
    tree = html.fromstring(r.text)
    payload['_csrf'] = tree.forms[0].fields['_csrf']

    r = session.post('https://portal.ncu.edu.tw/login', data=payload)
    
    r = session.get('https://classroom.csie.ncu.edu.tw/reserve.html')    #This whill redirect to https://classroom.csie.ncu.edu.tw/index.html
    # Get CSRF token from portal redirect form
    #print(r.url)
    tree = html.fromstring(r.text)
    token = tree.forms[0].fields['_csrf']

    payload2 = {
        'chineseName' : '資工系借教室系統',
        'englishName' : 'CSIE classroom',
        'scopes' : ['identifier','chinese-name'], 
        '_scope' : ['on','on'],
        "_csrf" : token
    }

    r = session.post('https://portal.ncu.edu.tw/oauth/leaving', data=payload2)
    
    return

def sign(session, classroom):
    Sign = {
        'cid': classroom["cid"],
        'phone': classroom["phone"],
        'teacher': classroom["teacher"],
        'start_period': classroom["start_period"],
        'end_period':  classroom["end_period"],
        'note': classroom["note"]
    }

    today=datetime.date.today()
    use_day=""

    try:
        use_day=classroom["date"][today.strftime("%Y-%m-%d")]+" 00:00:00"
    except:
        try:
            weekday = today.weekday()
            if(week[classroom["date"]["EVERY"]]==weekday):
                use_day = today + datetime.timedelta(days=14)
                use_day = use_day.strftime("%Y-%m-%d")+" 00:00:00"
        except:
            print("Date not found in config.")
            return False
    
    if(use_day!=""):
        Sign['date']=use_day
        print(Sign)
        headers2 = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-TW,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Connection': 'keep-alive',
            'Host': 'classroom.csie.ncu.edu.tw',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
        }

        r = session.get('https://classroom.csie.ncu.edu.tw/reserve.html',headers=headers2)
        # Sign
        r = session.post('https://classroom.csie.ncu.edu.tw/reserve', data=Sign)
    
        return True

    return False

if __name__ == '__main__':
    main()
