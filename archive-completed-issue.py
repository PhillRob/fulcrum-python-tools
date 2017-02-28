import logging
from datetime import datetime, timedelta

from fulcrum import Fulcrum

# variables
print('set variables')
formIdIssue = '52d56fc5-0a83-4912-a0aa-cbea3f8fc0ff'
# formIdTest = '345086c9-0add-4a4b-a458-62fbfef58743'# get form ID from fulcrum web app
apiToken = "magic api token"  # magic api token
urlBase = 'https://api.fulcrumapp.com/api/v2/'
fulcrum = Fulcrum(key=apiToken)
logging.basicConfig(filename='status-update.log', level=logging.DEBUG)
issueTimestamp = datetime.today() - timedelta(days=15)  # number of days as a delimiter

print('get issue data')
Issue = fulcrum.records.search(url_params={'form_id': formIdIssue})['records']

print('create issue dataframe for roads')
for record in Issue:
    if '9b3a' not in record['form_values']:
        # Issue[index]['osname'] = 'NA'
        print('No OS name field found')
    else:
        if (record['updated_at'] <= str(issueTimestamp)) & (record['status'] == "Completed"):
            # Issue[index]['osname'] = ''.join(Issue[index]['form_values']['9b3a'])
            record['status'] = "Archived"
            updatedRecord = fulcrum.records.update(record['id'], record)
            print(record['updated_at'], 'OS name found, older than', issueTimestamp, 'and status completed')
        else:
            print('Record not completed or younger than', issueTimestamp)
            record['osname'] = 'NA'
