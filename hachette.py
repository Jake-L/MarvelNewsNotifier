import os
from time import sleep
from datetime import datetime
from datetime import timedelta
import smtplib
from urllib.request import urlopen
import ssl

# create ssl settings for reading the url
ssl._create_default_https_context = ssl._create_unverified_context

email_addr = []
src_email = "marvelcollectionsnews@gmail.com"
title_list = []
first_run = True
INTERVAL = 900
email_file = "emails.txt"

print("Running script with email list: %s" % email_file)

# read the password from a text file
with open("password.txt", 'r') as f:
    PASSWORD = f.read().strip()

def sleep_before_checking():
    print("Will run again at %s" % (" ".join((datetime.now() + timedelta(seconds=INTERVAL)).ctime()[:-5].split())))
    sleep(INTERVAL)

while True:
    email_list = []
    # try to open the url, and restart the loop if it fails
    try:
        response = urlopen("https://www.hachettebookgroup.biz/search/?q=marvel&sort_by=-pub_date&results_per_page=100")
    except:
        print("Error accessing hachette site")
        sleep_before_checking()
        continue
    line_counter = -1

    # read every line from the webpage
    for rawline in response:
        line = rawline.decode('utf-8')

        # check for invalid date
        if 'On Sale Date:' in line:
            try:
                # convert the date string to a datetime object
                date_string = line.replace('On Sale Date:','').replace('Sept','Sep').replace('June','Jun').replace('July','Jul').replace('April','Apr').replace('March','Mar').replace('.','').strip()
                date_object = datetime.strptime(date_string, '%b %d, %Y')

                # restart if any date is before today
                if date_object < datetime.now():
                    print("ERROR: invalid dates in source data")
                    sleep_before_checking()
                    break
            except Exception as e:
                print(str(e))

        # this string appears 3 lines before the title
        if '<ul class="results-gallery">' in line:
            line_counter = 3

        if line_counter == 0:
            title = line.strip()

            if title not in title_list:
                title_list.append(title)

                # don't send emails on the first run
                if first_run == False:
                    email_list.append(title.replace('&amp;','&').replace('&#39;',"'"))

        if line_counter >= 0:
            line_counter -= 1
    first_run = False

    # send the email with the new titles
    if len(email_list) > 0:
        message = """Subject: {} new Marvel collections posted on hachette
{}
\nIf you wish to stop receiving these emails, reply "UNSUBSCRIBE"
""".format(len(email_list), "\n".join(email_list))
        
        # read the list of email addresses from a text file
        with open(email_file, 'r') as f:
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