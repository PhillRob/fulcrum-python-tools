import json
import logging
from datetime import datetime, timedelta

import requests
from fulcrum import Fulcrum

# TODO: get form list with id's
# assign variables
formId = 'your form ID'  # get form ID from fulcrum web app
days = 12
timestamp = datetime.today() - timedelta(days=days)  # number of days as a delimiter
apiToken = "your Api token"  # magic api token
urlBase = 'https://api.fulcrumapp.com/api/v2/'
fulcrum = Fulcrum(key=apiToken)
newlabel = 'Design'  # status label is set to this value
logging.basicConfig(filename='status-update.log', level=logging.DEBUG)


# define funtion that gets records that are older than 10 days
# TODO: refactor using "data = fulcrum.records.find(record_id)"

def getRecords(formId):
    params = {
        'form_id': formId,
        'updated_before': timestamp
    }
    headers = {'X-ApiToken': apiToken}
    response = requests.get(urlBase + 'records.json', headers=headers, params=params)
    responseDecoded = json.loads(response.text)
    if 'records' in responseDecoded:
        return responseDecoded
    else:
        return False


# TODO: loop this every day or use crontab

# get the records
records = getRecords(formId)['records']
logging.debug(print('Today (', datetime.today(), ')', len(records), 'Records are older than', days, 'days'))
if len(records) > 0:
    for record in records:
        record['status'] = newlabel
        updatedRecord = fulcrum.records.update(record['id'], record)
else:
    logging.debug('No records to update')
