# script for batch deletions

import math, json

from fulcrum import Fulcrum

# variables
with open("/credentials.json") as c:
	credentials = json.load(c)

fulcrum = Fulcrum(key=credentials['fulcrum_api'])
recordsPerPage = 5000

# get number of pages
recordCount = fulcrum.forms.find(credentials['TMO_TI_form'])['form']['record_count']
pages = math.ceil(recordCount / recordsPerPage)

# get data
data = []
for p in range(1, pages + 1):
	dataPage = fulcrum.records.search(
		url_params={'form_id': credentials['TMO_TI_form'], 'page': p, 'per_page': recordsPerPage})['records']
	data.extend(dataPage)

missmatch = match = 0

# this deletes everything, add a little bit of logic
for record in data:
	deleted = fulcrum.records.delete(record['id'])
	match = match + 1
	print(match)

