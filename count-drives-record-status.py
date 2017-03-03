import logging
from datetime import datetime, timedelta

import pandas as pd
from fulcrum import Fulcrum

# variables
formIdIssue = '52d56fc5-0a83-4912-a0aa-cbea3f8fc0ff'  # get form ID from fulcrum web app
# formIDAsset = 'bfe42feb-d940-4086-8de6-057a0e5ad211'
formIDAssetTest = 'a487599c-9adb-428a-a08b-cefe1d6138b9'
apiToken = ""  # magic api token
urlBase = 'https://api.fulcrumapp.com/api/v2/'
fulcrum = Fulcrum(key=apiToken)
logging.basicConfig(filename='status-update.log', level=logging.DEBUG)
osDays = 15
osTimestamp = datetime.today() - timedelta(days=osDays)  # number of days as a delimiter
rdDays = 30
rdTimestamp = datetime.today() - timedelta(days=rdDays)  # number of days as a delimiter

# change status for 'side median' and 'planted streets'
## get issue data
### to group per open space we use the 'select_os_' field
# todo: one set of issues and assets for 'side medieans' and 'plantend streets' with a status change of 4 weeks
Issue = fulcrum.records.search(url_params={'form_id': formIdIssue})['records']
# create new element for osname
for index in range(len(Issue)):
    if (Issue[index]['created_at'] >= str(rdDays)):
        if '9b3a' not in Issue[index]['form_values']:
            Issue[index]['osname'] = 'NA'
        else:
            Issue[index]['osname'] = ''.join(Issue[index]['form_values']['9b3a'])
    else:
        logging.debug('Record to old')
        Issue[index]['osname'] = 'NA'

Issuedf = pd.DataFrame(Issue)

# get asset data and create new element for osname
Asset = fulcrum.records.search(url_params={'form_id': formIDAssetTest})['records']
# todo: only get records from 'side medieans' and 'plantend streets'
# Assetdf = pd.DataFrame(Asset)
# this just favorises the drama, 1 action required 2, approval requirec and 3 completion

Issuedf1 = Issuedf[(Issuedf.osname != 'NA')]
g = Issuedf1.drop_duplicates(subset=['status', 'osname'])

# g1 = g[['osname', 'status']].sort(columns=['osname', 'status'])
g2 = g[['osname', 'status']]
g3 = g2[(g2.status == 'Action required')]
g4 = g2[(g2.status == 'Request for approval') & (g2['osname'].isin(g3.osname) == False)]
g5 = g2[(g2.status == 'Completed') & (g2['osname'].isin(g3.osname) == False) & (g2['osname'].isin(g4.osname) == False)]
g6 = g3.append(g4)
g6 = g6.append(g5)
# Issuedf1.status.unique()
# update records in assets according to g6 data frame
for record in Asset:
    if '9c5d' in record['form_values']:
        logging.debug('OS name:', ''.join(record['form_values']['9c5d']['choice_values']), 'found')
    else:
        logging.debug('OS name field empty')
    if any(x in ''.join(record['form_values']['9c5d']['choice_values']) for x in g6.osname) & any(
                    x in ''.join(record['status']) for x in
                    g6[(g6.osname == ''.join(record['form_values']['9c5d']['choice_values']))]['status']):
        logging.debug(g6[(g6.osname == ''.join(record['form_values']['9c5d']['choice_values']))]['osname'],
                      'already has status',
                      g6[(g6.osname == ''.join(record['form_values']['9c5d']['choice_values']))]['status'])
    else:
        if any(x in ''.join(record['form_values']['9c5d']['choice_values']) for x in g6.osname):
            logging.debug(
                (''.join(record['form_values']['9c5d']['choice_values']), "will change status from", record['status']))
            record['status'] = ''.join(
                g6[(g6['osname'].str.contains(''.join(record['form_values']['9c5d']['choice_values'])))]['status'])
            logging.debug(('New status:', record['status']))
            updatedRecord = fulcrum.records.update(record['id'], record)
        else:
            if record['status'] == 'Not inspected':
                logging.debug('No change required')
            else:
                logging.debug((''.join(record['form_values']['9c5d']['choice_values']), 'is set to Not inspected'))
                record['status'] = 'Not inspected'
                updatedRecord = fulcrum.records.update(record['id'], record)


# todo: new chunk of issues and assets for all other open spaces with a status change of 2 weeks
# TODO: update readme
