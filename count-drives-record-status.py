# -*- coding: UTF-8 -*-
import logging
from datetime import datetime

import pandas as pd
from fulcrum import Fulcrum

# variables
print('set variables')
formIdIssue = '52d56fc5-0a83-4912-a0aa-cbea3f8fc0ff'  # get form ID from fulcrum web app
formIDAsset = 'bfe42feb-d940-4086-8de6-057a0e5ad211'
# formIDAssetTest = 'a487599c-9adb-428a-a08b-cefe1d6138b9'
apiToken = ""  # magic api token
urlBase = 'https://api.fulcrumapp.com/api/v2/'
fulcrum = Fulcrum(key=apiToken)
logging.basicConfig(filename='amn-asset-status-update.log', level=logging.DEBUG)
logging.debug(str(datetime.today()))

# get asset data
logging.debug('get asset data')
Asset = fulcrum.records.search(url_params={'form_id': formIDAsset})['records']

# get issue data
logging.debug('get issue data')
Issue = fulcrum.records.search(url_params={'form_id': formIdIssue})['records']

# create new element for osname 5098 Issue[index]['form_values']['5098'][0]['record_id']
print('create issue dataframe for roads')
for record in Issue:
    if '5098' in record['form_values']:
        record['os'] = record['form_values']['5098'][0]['record_id']
    else:
        print(record)

Issuedf = pd.DataFrame(Issue)
Issuedf = Issuedf.drop_duplicates(subset=['status', 'os'])[['status', 'os']]
Issuedf = Issuedf.dropna(how='any')

Issuedf.status[Issuedf.status == 'On Hold'] = 'Action required'
Issuedf.status[Issuedf.status == 'On Hold (AMN)'] = 'Action required'
Issuedf.status[Issuedf.status == 'Re-inspection required '] = 'Action required'
Issuedf = Issuedf.drop_duplicates(subset=['status', 'os'])[['status', 'os']]

Issuedf1 = Issuedf[(Issuedf.status == 'Action required')]
Issuedf2 = Issuedf[(Issuedf.status == 'Request for approval') & (-Issuedf.os.isin(Issuedf1.os))]

Issuedf3 = Issuedf[
    (Issuedf.status == 'Completed') & (-Issuedf.os.isin(Issuedf1.os)) & (-Issuedf.os.isin(Issuedf2.os))]

ostoupdate = Issuedf1.append(Issuedf2)
ostoupdate = ostoupdate.append(Issuedf3)

for record in Asset:
    print('record id', ''.join(record['id']), 'found')
    updateinfo = (''.join(ostoupdate[(ostoupdate['os'] == ''.join(record['id']))]['status']))
    if len(updateinfo) > 0:
        print('Asset has issue information')
        if updateinfo == record['status']:
            print('Asset status', record['status'], 'matches', updateinfo, '. So no change is required. ')
        if updateinfo != record['status']:
            record['status'] = updateinfo
            print('Asset status', record['status'], 'will be updated to ', updateinfo)
    else:
        if record['status'] != 'Not inspected':
            print('Asset does not have issues recorded and will be set to Not inspected')
            # record['status'] = 'Not inspected'
        else:
            print('Asset does not have issues and is already set to not inspected. Nothing do to here. ')
            record['status'] = updateinfo['status']
    updatedRecord = fulcrum.records.update(record['id'], record)
