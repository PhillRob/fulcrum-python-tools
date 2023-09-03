#!/usr/bin/python3
# -*- coding: UTF-8 -*-

# # # imports
import gc, json
import logging
import math
import os
import smtplib
import time
from collections import Counter
from datetime import datetime, timedelta
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from fulcrum import Fulcrum

# fulcrum vars
with open("production/credentials.json") as c:
	credentials = json.load(c)

logging.basicConfig(filename='production/fulcrum-mailer-v2.log', level=logging.DEBUG)

# dates
weektimestamp = datetime.today() - timedelta(days=7)  # number of days as a delimiter
monthtimestamp = datetime.today() - timedelta(days=30)  # number of days as a delimiter
today = datetime.today()
weeknumber = time.strftime("%U")
# no_timeout = Timeout(connect=None, read=None)
# http = PoolManager(timeout=no_timeout)

# general smtp mailer vars
fromaddr = credentials['from_address']
ImgFileName = "bpla-systems.png"
img_data = open(ImgFileName, 'rb').read()
sendtest = True
recordsPerPage = 5000


def TMO_TI_email(test):
	fulcrum = Fulcrum(key=credentials['fulcrum_api'])

	# recipients list
	if test:
		addr = ['robeck@bp-la.com', 'philipp.robeck@gmail.com', 'phill@gmx.li']
	else:
		addr = ['tmo@bp-la.com']

	# WS Construction Management
	# get project vars
	formid = credentials['TMO_TI_form']

	# get number of pages
	recordCount = fulcrum.forms.find(formid)['form']['record_count']
	pages = math.ceil(recordCount / recordsPerPage)

	## get data per page
	data = []
	for p in range(1, pages + 1):
		dataPage = fulcrum.records.search(
			url_params={'form_id': credentials['TMO_TI_form'], 'page': p, 'per_page': 7000})['records']
		data.extend(dataPage)

	# get unique project IDs in a list
	projectList = list()
	for record in data:
		projectId = record['project_id']
		if projectId not in projectList:
			projectList.append(projectId)

	# create dict with matching names
	result = {}
	for i in projectList:
		try:
			projectInfo = fulcrum.projects.find(i)['project']
			result[i] = projectInfo['name']
		except:
			result[i] = 'Unknown Project'

	# add project names to org data
	for record in data:
		record['project'] = result.get(record['project_id'], 'Unknown')

	packagedict = {}
	resultdpplain = []

	for record in data:
		my_dictdp = record.get('project')
		resultdpplain.append(my_dictdp)
	resultdpplain = ['None' if v is None else v for v in resultdpplain]
	dptextplaint = Counter(resultdpplain)

	# week count created per package
	weekpackagecreated = []
	for record in data:
		if record['created_at'] >= str(weektimestamp):
			my_dict_week = record.get('project')
			weekpackagecreated.append(my_dict_week)
	weekpackagecreated = ['None' if v is None else v for v in weekpackagecreated]
	packagedict[0] = dict(Counter(weekpackagecreated))

	# week count updated per package
	weekpackageupdated = []
	for record in data:
		if record['updated_at'] >= str(weektimestamp):
			my_dict_weekupdated = record.get('project')
			weekpackageupdated.append(my_dict_weekupdated)
	weekpackageupdated = ['None' if v is None else v for v in weekpackageupdated]
	packagedict[1] = dict(Counter(weekpackageupdated))

	packagedict[2] = dict(dptextplaint)
	dptextplain = str(dptextplaint)
	dptextplain = dptextplain.replace(',', '\r\n')
	dptextplain = dptextplain.replace('Counter({', '')
	dptextplain = dptextplain.replace('})', '')
	dptextplain = dptextplain.replace('\'', '')

	dictall = packagedict[0], packagedict[1], packagedict[2]
	dictall = {k: [d.get(k) for d in dictall] for k in {k for d in dictall for k in d}}
	dictall = dict(sorted(dictall.items()))

	dptext = str(dictall)
	dptext = dptext.replace("{'", '<tr><th scope="row">')
	dptext = dptext.replace("\': [", '</th><td>')
	dptext = dptext.replace(", \'", '<tr><th scope="row">')
	dptext = dptext.replace(", ", '</td><td>')
	dptext = dptext.replace("]", '</td></tr>')
	dptext = dptext.replace("}", '')
	dptext = dptext.replace(" [", '</td><td>')
	dptext = dptext.replace("None:", 'None')

	# total count
	result = []
	for record in data:
		my_dict = record.get('status')
		my_dict = my_dict.split(' - ', 1)[0]
		result.append(my_dict)

	statustotalcount = Counter(result)
	totalcount = len(data)

	totaltext = str(statustotalcount)
	totaltext = totaltext.replace(',', '</li><li>')
	totaltext = totaltext.replace('Counter({', '<ul><li>')
	totaltext = totaltext.replace('})', '</li></ul>')
	totaltext = totaltext.replace('\'', '')

	# week count created
	resultweek = []
	for record in data:
		if record['created_at'] >= str(weektimestamp):
			my_dict_week = record.get('status')
			resultweek.append(my_dict_week)
	statusweekcount = Counter(resultweek)
	weekcount = sum(statusweekcount.values())

	# week count updated
	resultweekupdated = []
	for record in data:
		if record['updated_at'] >= str(weektimestamp):
			my_dict_weekupdated = record.get('status')
			resultweekupdated.append(my_dict_weekupdated)
	statusweekcountupdated = Counter(resultweekupdated)
	weekcountupdated = sum(statusweekcountupdated.values())

	# mail vars
	msgRoot = MIMEMultipart('related')
	msgRoot['From'] = fromaddr
	msgRoot['To'] = ','.join(addr)
	msgRoot['Subject'] = ("TMO Tree Inventory - Summary Week " + weeknumber)
	msgRoot.preamble = 'This is a multi-part message in MIME format.'

	# Encapsulate the plain and HTML versions of the message body in an
	# 'alternative' part, so message agents can decide which they want to display.
	msgAlternative = MIMEMultipart('alternative')
	msgRoot.attach(msgAlternative)

	# Next, we attach the body of the email to the MIME message:
	msgText = MIMEText(
		"Dear all, \r\n attached the summary for week %s (%s to %s) of the TMO Tree Inventory. \r\n \r\n Total number of trees: %s  \r\n \r\n %s \r\n \r\n Trees recorded this week: %s \r\n Trees inspected and updated this week: %s \r\n \r\n Trees per project \r\n %s \r\n \r\n This email is sent automatically on a weekly basis. \r\n \r\n Please contact mailer@bp-la.com for any feedback and comments. \r\n \r\n Kind regards \r\n BPLA \r\n www.bp-la.com \r\n \r\n" % (
			weeknumber, weektimestamp.strftime('%d.%m.%Y'), today.strftime('%d.%m.%Y'), totalcount, totaltext,
			weekcount,
			weekcountupdated, dptextplain))

	msgAlternative.attach(msgText)

	msgText = MIMEText(
		'<!doctype html><style>table {font-family: arial, sans-serif; border-collapse: collapse;width:400}td, th {border: 1px solid #dddddd; text-align: left; padding: 8px; }tr:nth-child(even) {background-color: #dddddd;}</style><html><head></head><body><br>Dear all,</br><p>attached the summary for week %s (%s to %s) of the TMO Tree Inventory. </p></b><p><h2>Total number of trees: %s</h2></b>	%sTotal trees recorded this week: %s <br>Total trees inspected and updated this week: %s </p><br><h2>Trees per project and week</h2><table width="400" border="0"><col align="left"><col align="left"><col align="left"><col align="left"><tbody><tr>      <th scope="row">Project</th>      <td>Created</td>      <td>Updated</td>  <td>Total</td>   </tr>  %s  </tbody></table>	<br><br> This email is sent automatically on a weekly basis. <br><br> Please contact <a href="mailto:mailer@bp-la.com" target="new">mailer@bp-la.com</a> for any feedback and comments. <br><br>	Kind regards <br>BPLA  <br><a href="http://www.bp-la.com" target="_blank">www.bp-la.com</a><br><br><img src="cid:image1"></body>' % (
			weeknumber, weektimestamp.strftime('%d.%m.%Y'), today.strftime('%d.%m.%Y'), totalcount, totaltext,
			weekcount,
			weekcountupdated, dptext), 'html')

	msgAlternative.attach(msgText)

	# This example assumes the image is in the current directory
	fp = open(ImgFileName, 'rb')
	msgImage = MIMEImage(fp.read())
	fp.close()

	# Define the image's ID as referenced above
	msgImage.add_header('Content-ID', '<image1>')
	msgRoot.attach(msgImage)

	# For sending the mail, we have to convert the object to a string, and then use the same prodecure as above to send
	# using the SMTP server.
	server = smtplib.SMTP(credentials['smtp'], credentials['smtp_port'])
	server.starttls()
	server.ehlo()
	server.login(fromaddr, credentials['email_pwd'])
	server.sendmail(fromaddr, addr, msgRoot.as_string())
	server.quit()
	gc.collect()

TMO_TI_email(test=sendtest)
