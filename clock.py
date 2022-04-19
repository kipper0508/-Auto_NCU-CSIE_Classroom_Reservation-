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

def error_message(message):
    print("\033[1;31mError:",end=" ")
    print("\033[1;39m",end=" ")
    print(message)
    
def main():
    with open(args.config,encoding='utf-8-sig') as config_file:
        config = json.load(config_file)

    #Check EVERY and target mode together?
    if(len(config["rooms"][args.classroom]['date'])>1 and "EVERY" in config["rooms"][args.classroom]['date'] ):
        print("\033[1;33mWarning:",end=" ")
        print("\033[1;39mYou are using EVERY tag and target day mode together")
    
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

    if(login(session, headers, config['account'], config['password'])):
        #reserversion
        if(sign(session, config["rooms"][args.classroom])):
            print("\033[1;32mSucess")
    

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

    #login to NCU portal
    r = session.post('https://portal.ncu.edu.tw/login', data=payload)   
    
    if(r.url=="https://portal.ncu.edu.tw/login"):
        error_message("Your config about account or password is not set properly")
        return False
        
    # redirect to https://classroom.csie.ncu.edu.tw/index.html but need to auth from portal
    r = session.get('https://classroom.csie.ncu.edu.tw/reserve.html')

    # Get CSRF token from portal redirect form
    tree = html.fromstring(r.text)
    token = tree.forms[0].fields['_csrf']

    payload2 = {
        'chineseName' : '資工系借教室系統',
        'englishName' : 'CSIE classroom',
        'scopes' : ['identifier','chinese-name'], 
        '_scope' : ['on','on'],
        "_csrf" : token
    }

    # post auth to portal
    r = session.post('https://portal.ncu.edu.tw/oauth/leaving', data=payload2)
    
    return True

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
    use_day="" #the day you want to use classroom

    # First check is today the target to do a reservation
    if( today.strftime("%Y-%m-%d") in classroom["date"] ):
        use_day=classroom["date"][today.strftime("%Y-%m-%d")]+" 00:00:00"
    elif("EVERY" in classroom["date"] ):
        weekday = today.weekday()
        use_day = today + datetime.timedelta(days=14)
        use_day = use_day.strftime("%Y-%m-%d")+" 00:00:00"
    else:
        error_message("Date not found in config.")
        return False
    
    # if use_day is empty, means today is not fount in config 
    Sign['date']=use_day

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

    
    if(r.text=="時間與其他預約重疊"):
        error_message("The time you want has been reserved by others")
        return False
    elif(r.text!="OK"):
        error_message("Your config about rooms is not set properly")
        return False
        
    return True  

if __name__ == '__main__':
    main()
