import os
from time import sleep
from datetime import datetime
from datetime import timedelta
import smtplib
from urllib.request import urlopen

email_addr = []
src_email = "marvelcollectionsnews@gmail.com"
title_list = []
email_list = []
first_run = True
INTERVAL = 900

with open("password.txt", 'r') as f:
    PASSWORD = f.read().strip()

def sleep_before_checking():
    print("Will run again at %s" % (" ".join((datetime.now() + timedelta(seconds=INTERVAL)).ctime()[:-5].split())))
    sleep(INTERVAL)

while True:
    email_list = []
    try:
        response = urlopen("https://www.hachettebookgroup.biz/search/?q=marvel&sort_by=-pub_date&results_per_page=100")
    except:
        print("Error accessing hachette site")
        sleep_before_checking()
        continue
    line_counter = -1
    for rawline in response:
        line = str( rawline, encoding='utf8' )
        if '<ul class="results-gallery">' in line:
            line_counter = 3

        if line_counter == 0:
            title = line.strip()

            if title not in title_list:
                title_list.append(title)

                if first_run == False:
                    email_list.append(title.replace('&amp;','&'))

        if line_counter >= 0:
            line_counter -= 1
    first_run = False

    # send the email with the new titles
    if len(email_list) > 0:
        message = 'Subject: {} new Marvel collections posted on hachette\n\n{}\n\nIf you wish to stop receiving these emails, reply "UNSUBSCRIBE"'.format(len(email_list), "\n".join(email_list))

        # read the list of email addresses from a text file
        with open("emails.txt", 'r') as f:
            email_addr = f.read().splitlines()
            
        print("send email for {} new titles to {} users".format(len(email_list), len(email_addr)))

        # send the email
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(src_email, PASSWORD)
                server.sendmail(src_email, email_addr, message)
        except:
            print("Error sending emails")
            sleep_before_checking()
            continue
    else:
        print("no new titles")

    sleep_before_checking()