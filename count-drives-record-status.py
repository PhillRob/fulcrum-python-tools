import logging

import pandas as pd
from fulcrum import Fulcrum

# var
formIdIssue = '52d56fc5-0a83-4912-a0aa-cbea3f8fc0ff'  # get form ID from fulcrum web app
# formIDAsset = 'bfe42feb-d940-4086-8de6-057a0e5ad211'
formIDAssetTest = 'a487599c-9adb-428a-a08b-cefe1d6138b9'
# days = 12
# timestamp = datetime.today() - timedelta(days=days)  # number of days as a delimiter
apiToken = "2ef04ab67ab414b7ac6c7815235ace6f9cdf3ab79b9e0874beb053a9dfa9bb682d7bbd1a3117b68e"  # magic api token
urlBase = 'https://api.fulcrumapp.com/api/v2/'
fulcrum = Fulcrum(key=apiToken)
logging.basicConfig(filename='status-update.log', level=logging.DEBUG)

# get Isseu data
# todo: we have to choose the field for the data summary! '9b3a' is the seletor field the other one used below is the pre selector that mismatches '9b3a'

Issue = fulcrum.records.search(url_params={'form_id': '52d56fc5-0a83-4912-a0aa-cbea3f8fc0ff'})['records']
# create new element for osname
for index in range(len(Issue)):
    print(index)
    if '9b3a' not in Issue[index]['form_values']:
        Issue[index]['osname'] = 'NA'
    else:
        Issue[index]['osname'] = ''.join(Issue[index]['form_values']['9b3a'])
    print(Issue[index]['osname'])

Issuedf = pd.DataFrame(Issue)

# get asset data and create new element for osname
Asset = fulcrum.records.search(url_params={'form_id': 'a487599c-9adb-428a-a08b-cefe1d6138b9'})['records']
for index in range(len(Asset)):
    print(index)
    if '9c5d' not in Asset[index]['form_values']:
        Asset[index]['osname'] = 'NA'
    else:
        Asset[index]['osname'] = ''.join(Asset[index]['form_values']['9c5d']['choice_values'])
    print(Asset[index]['osname'])

# Assetdf = pd.DataFrame(Asset)
# Assetdf['osname'] = Assetdf['osname'].str[0]
# todo: compare curent openspace status w/ most frequent status suggested by issue
# this just favorises the drama, 1 action required 2, approval requirec and 3 completion

g = Issuedf.drop_duplicates(subset=['status', 'osname'])
g1 = g[['osname', 'status']].sort(columns=['osname', 'status'])
g2 = g1[['osname', 'status']]
g3 = g2[(g2.status == 'Action required')]

g4 = g2[(g2.status == 'Request for approval') & (g2['osname'].isin(g3.osname) == False)]
g5 = g2[(g2.status == 'Completed') & (g2['osname'].isin(g3.osname) == False) & (g2['osname'].isin(g4.osname) == False)]
g6 = g3.append(g4)
g6 = g6.append(g5)

aa = \
    Issuedf[Issuedf['osname'].str.contains('Bilal bin Rabah ')]['form_values']

# AssetUpdate = Assetdf[(Assetdf['osname'].isin(g6['osname']))]
# AssetUpdate = Asset[(Asset[['osname']].isin(g6['osname']))]
# todo: change differing status
# this works
for record in Asset:
    if '9c5d' in record['form_values']:
        # we use this:
        print('OS name field found. OS name:', ''.join(record['form_values']['9c5d']['choice_values']))
    # print(''.join(record['form_values']['9c5d']['choice_values']))
    else:
        print('OS name field empty')
    # print(Asset[record]['osname'])
    # if g6.osname.str.contains(Asset[index]['osname']):
    # if any(x in record['osname'] for x in g6.osname):
    if any(x in ''.join(record['form_values']['9c5d']['choice_values']) for x in g6.osname):
        print(''.join(record['form_values']['9c5d']['choice_values']), "will change status from", record['status'])
        # print(record['status'], "will change change status");
        # print(Asset[record]['osname']);
        record['status'] = ''.join(
            g6[(g6['osname'].str.contains(r''.join(record['form_values']['9c5d']['choice_values'])))]['status'])
        # print(g6[(g6['osname'].str.contains(Asset[record]['osname']))]['status'])
        print('New status:', record['status']);
        # del record['osname']

        updatedRecord = fulcrum.records.update(record['id'], record)
    else:
        logging.debug('No records to update')



# todo: update readme
