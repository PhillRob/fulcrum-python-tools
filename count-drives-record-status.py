import logging

import pandas as pd
from fulcrum import Fulcrum

# variables
formIdIssue = '52d56fc5-0a83-4912-a0aa-cbea3f8fc0ff'  # get form ID from fulcrum web app
# formIDAsset = 'bfe42feb-d940-4086-8de6-057a0e5ad211'
formIDAssetTest = 'a487599c-9adb-428a-a08b-cefe1d6138b9'
apiToken = "your api token"  # magic api token
urlBase = 'https://api.fulcrumapp.com/api/v2/'
fulcrum = Fulcrum(key=apiToken)
logging.basicConfig(filename='status-update.log', level=logging.DEBUG)

# get issue data
# TODO: we have to choose the field for the data summary! '9b3a' is the seletor field the other one used below is the pre selector that mismatches '9b3a'

Issue = fulcrum.records.search(url_params={'form_id': formIdIssue})['records']
# create new element for osname
for index in range(len(Issue)):
    if '9b3a' not in Issue[index]['form_values']:
        Issue[index]['osname'] = 'NA'
    else:
        Issue[index]['osname'] = ''.join(Issue[index]['form_values']['9b3a'])
Issuedf = pd.DataFrame(Issue)

# get asset data and create new element for osname
Asset = fulcrum.records.search(url_params={'form_id': formIDAssetTest})['records']

# Assetdf = pd.DataFrame(Asset)
# this just favorises the drama, 1 action required 2, approval requirec and 3 completion

g = Issuedf.drop_duplicates(subset=['status', 'osname'])
# g1 = g[['osname', 'status']].sort(columns=['osname', 'status'])
g2 = g[['osname', 'status']]
g3 = g2[(g2.status == 'Action required')]
g4 = g2[(g2.status == 'Request for approval') & (g2['osname'].isin(g3.osname) == False)]
g5 = g2[(g2.status == 'Completed') & (g2['osname'].isin(g3.osname) == False) & (g2['osname'].isin(g4.osname) == False)]
g6 = g3.append(g4)
g6 = g6.append(g5)

# update records in assets according to g6 data frame
for record in Asset:
    if '9c5d' in record['form_values']:
        logging.debug(print('OS name field found. OS name:', ''.join(record['form_values']['9c5d']['choice_values'])))
    else:
        logging.debug(print('OS name field empty'))
    if any(x in ''.join(record['form_values']['9c5d']['choice_values']) for x in g6.osname):
        logging.debug(
            print(''.join(record['form_values']['9c5d']['choice_values']), "will change status from", record['status']))
        record['status'] = ''.join(
            g6[(g6['osname'].str.contains(r''.join(record['form_values']['9c5d']['choice_values'])))]['status'])
        logging.debug(print('New status:', record['status']))
        updatedRecord = fulcrum.records.update(record['id'], record)
    else:
        logging.debug('No records to update')
# TODO: update readme
