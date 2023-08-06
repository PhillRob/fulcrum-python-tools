# script for batch deletions

import math, json

from fulcrum import Fulcrum

# variables
with open("/credentials.json") as c:
	credentials = json.load(c)

fulcrum = Fulcrum(key=credentials['fulcrum_api'])

# fuclrum from
formID = "6d9c5cdf-f947-48b8-9a99-0ec49b492d77"
formdata = fulcrum.forms.find(formID)
recordsPerPage = 5000

# get number of pages
recordCount = fulcrum.forms.find(formID)['form']['record_count']
pages = math.ceil(recordCount / recordsPerPage)

# get data
if pages > 1:
	for p in range(1, pages + 1):
		dataPage = fulcrum.records.search(url_params={'form_id': formID, 'page': p, 'per_page': recordsPerPage})[
			'records']
		if p > 1:
			data.extend(dataPage)
		else:
			data = dataPage
else:
	data = fulcrum.records.search(url_params={'form_id': formID, 'page': 1, 'per_page': recordsPerPage})['records']

noloc = missmatch = match = 0

for record in data:
	deleted = fulcrum.records.delete(record['id'])
	match = match+1
	print(match)


