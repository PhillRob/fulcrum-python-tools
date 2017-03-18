import logging
from datetime import datetime, timedelta

from fulcrum import Fulcrum

# variables ##thum
print('set variables')
formIdIssue = '58172326-272a-49d8-916e-7a893fd52dd4'
# formIdTest = '345086c9-0add-4a4b-a458-62fbfef58743'# get form ID from fulcrum web app
apiToken = "2ef04ab67ab414b7ac6c7815235ace6f9cdf3ab79b9e0874beb053a9dfa9bb682d7bbd1a3117b68e"  # magic api token
urlBase = 'https://api.fulcrumapp.com/api/v2/'
fulcrum = Fulcrum(key=apiToken)
logging.basicConfig(filename='thm-issue-status-update.log', level=logging.DEBUG)
issueTimestamp = datetime.today() - timedelta(days=15)  # number of days as a delimiter

print('get issue data')
Issue = fulcrum.records.search(url_params={'form_id': formIdIssue})['records']

print('create issue dataframe for roads')
for record in Issue:
    if record['status'] == "Archived":
        print("already archived")
    else:
        if (record['updated_at'] <= str(issueTimestamp)) & (record['status'] == "No Action Required"):
            record['status'] = "Archived"
            updatedRecord = fulcrum.records.update(record['id'], record)
            print(record['updated_at'], 'older than', issueTimestamp, 'and status no action required')
        else:
            print('Record not completed or younger than', issueTimestamp)
