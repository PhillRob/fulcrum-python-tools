# imports
import logging
import os
import smtplib
import time
from collections import Counter
from datetime import datetime, timedelta
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from fulcrum import Fulcrum

# fulcrum vars BPLA
apiToken = "magic api token"  # magic api token
urlBase = 'https://api.fulcrumapp.com/api/v2/'
fulcrum = Fulcrum(key=apiToken)
logging.basicConfig(filename='fulcrummailer.log', level=logging.DEBUG)
weektimestamp = datetime.today() - timedelta(days=7)  # number of days as a delimiter
today = datetime.today()
weeknumber = time.strftime("%U")

# general smtp mailer vars
fromaddr = "senderAdress@gmail.com" #replace w/ your sender adress
ImgFileName = "logo.jpg" # replace with your logo/image for signature
img_data = open(ImgFileName, 'rb').read()

# get project vars
formID = "formID" # replace with your from ID

# recipients list
WHTMaddr = ['email@adress.com','more@adress.com']

# get records
data = fulcrum.records.search(url_params={'form_id': formID})['records']

# total count
## this just counts records according to the status
result = []
for record in data:
    my_dict = {}
    my_dict = record.get('status')
    result.append(my_dict)
statustotalcount = Counter(result)
totalcount = len(data)

# week count created
## this counts records created over the last week
resultweek = []
for record in data:
    my_dict_week = {}
    if (record['created_at'] >= str(weektimestamp)):
        my_dict_week = record.get('status')
        resultweek.append(my_dict_week)
statusweekcount = Counter(resultweek)
weekcount = sum(statusweekcount.values())

# week count updated
## this counts records updated over the last week
resultweekupdated = []
for record in data:
    my_dict_weekupdated = {}
    if (record['updated_at'] >= str(weektimestamp)):
        my_dict_weekupdated = record.get('status')
        resultweekupdated.append(my_dict_weekupdated)
statusweekcountupdated = Counter(resultweekupdated)
weekcountupdated = sum(statusweekcountupdated.values())

# mail vars
msg = MIMEMultipart()
msg['From'] = fromaddr
msg['To'] = ','.join(WHTMaddr)
msg['Subject'] = ("Activity Summary Week " + weeknumber)

# Next, we attach the body of the email to the MIME message:
body = (
    "Dear all, \r\n attached the activity summary for week %s (%s to %s) .   \r\n \r\n Total number of records: %s  \r\n \r\n Records with status A: %s \r\n  Records with status B: %s \r\n \r\n \r\n Record created this week: %s \r\n Records updated this week: %s \r\n \r\n This email is sent automatically on a weekly basis. \r\n \r\n Kind regards." % (
        weeknumber, weektimestamp.strftime('%d.%m.%Y'), today.strftime('%d.%m.%Y'), totalcount, statustotalcount['2'],
        statustotalcount['1'], statustotalcount['4'], statustotalcount['3'], weekcount, weekcountupdated))
        # 1, 2, etc. reflect your status labels. prob. need to adjust those. 
msg.attach(MIMEText(body, 'plain'))
image = MIMEImage(img_data, name=os.path.basename(ImgFileName))
msg.attach(image)

# For sending the mail, we have to convert the object to a string, and then use the same prodecure as above to send using the SMTP server..
server = smtplib.SMTP('smtp.1und1.de', 587)
server.ehlo()
server.starttls()
server.ehlo()
server.login(fromaddr, "password") # add password
text = msg.as_string()
server.sendmail(fromaddr, WHTMaddr, text)
server.quit()

