import json
import logging
from datetime import datetime, timedelta

from fulcrum import Fulcrum

# variables
print('set variables')
formIdIssue = '58172326-272a-49d8-916e-7a893fd52dd4'  # get form ID from fulcrum web app

with open("credentials.json") as c:
	credentials = json.load(c)

urlBase = credentials['fulcrum_url']
fulcrum = Fulcrum(key=credentials['fulcrum_api'])

logging.basicConfig(filename='issue-status-update.log', level=logging.DEBUG)
issueTimestamp = datetime.today() - timedelta(days=15)  # number of days as a delimiter

print('get issue data')
data = []
for p in range(1, pages + 1):
	dataPage = fulcrum.records.search(
        url_params={'form_id': credentials['TMO_TI_form'], 'page': p, 'per_page': 5000})['records']
	data.extend(dataPage)

print('create issue dataframe for roads')
for record in data:
	if record['status'] == "Archived":
		print("already archived")
	else:
		if (record['updated_at'] <= str(issueTimestamp)) & (record['status'] == "No Action Required"):
			record['status'] = "Archived"
			updatedRecord = fulcrum.records.update(record['id'], record)
			print(record['updated_at'], 'older than', issueTimestamp, 'and status no action required')
		else:
			print('Record not completed or younger than', issueTimestamp)
