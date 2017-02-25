import logging
from datetime import datetime, timedelta

import pandas as pd
from fulcrum import Fulcrum

# variables
print('set variables')
formIdIssue = '52d56fc5-0a83-4912-a0aa-cbea3f8fc0ff'  # get form ID from fulcrum web app
# formIDAsset = 'bfe42feb-d940-4086-8de6-057a0e5ad211'
formIDAssetTest = 'a487599c-9adb-428a-a08b-cefe1d6138b9'
apiToken = "addapitoken"  # magic api token
urlBase = 'https://api.fulcrumapp.com/api/v2/'
fulcrum = Fulcrum(key=apiToken)
logging.basicConfig(filename='status-update.log', level=logging.DEBUG)
osDays = 15
osTimestamp = datetime.today() - timedelta(days=osDays)  # number of days as a delimiter
rdDays = 30
rdTimestamp = datetime.today() - timedelta(days=rdDays)  # number of days as a delimiter
road = ['Sidemedian roadside - مثلثات و مستطيلات', 'Planted street - شوارع مزروعة']
os = ['Bar hat - برحات', 'Exits/coverleaf - مخرج - ميدان', 'Garden - حديقة', 'King Salman Oasis - واحة الملك سلمان',
      'Park - منتزه', 'Playground - ملاعب أطفال', 'Sport facility - منشآت رياضية']

print('update roads')
# get asset data
print('get asset data')
Asset = fulcrum.records.search(url_params={'form_id': formIDAssetTest})['records']

# get issue data
print('get issue data')
Issue = fulcrum.records.search(url_params={'form_id': formIdIssue})['records']
IssueRd = IssueOs = Issue
# IssueOs = Issue

# to group per open space we use the 'select_os_' field
# lets do the roads
# todo: one set of issues and assets for 'side medieans' and 'plantend streets' with a status change of 4 weeks

# create new element for osname
print('create issue dataframe for roads')
for index in range(len(IssueRd)):
    if '9b3a' not in IssueRd[index]['form_values']:
        IssueRd[index]['osname'] = 'NA'
        IssueRd[index]['ostype'] = 'NA'
        logging.debug('No OS name field found')
    else:
        if IssueRd[index]['created_at'] >= str(rdTimestamp):  # todo: second condition
            IssueRd[index]['osname'] = ''.join(IssueRd[index]['form_values']['9b3a'])
            IssueRd[index]['ostype'] = ''.join(IssueRd[index]['form_values']['e910']['choice_values'])
            logging.debug('OS name found and additional colums created')
        else:
            logging.debug('Record to old')
            IssueRd[index]['osname'] = 'NA'
            IssueRd[index]['ostype'] = 'NA'

IssueRd = pd.DataFrame(IssueRd)
# this just favorises the drama, 1 action required 2, approval requirec and 3 completion

IssueRd = IssueRd[(IssueRd.osname != 'NA')]
IssueRd = IssueRd[(IssueRd['ostype'].isin(road))]
# IssuedfRd['ostype'].unique()
IssueRd['osname'] = pd.core.strings.str_strip(IssueRd['osname'])
g = IssueRd.drop_duplicates(subset=['status', 'osname'])
g2 = g[['osname', 'status']]
g3 = g2[(g2.status == 'Action required')]
g4 = g2[(g2.status == 'Request for approval') & (g2['osname'].isin(g3.osname) == False)]
g5 = g2[
    (g2.status == 'Completed') & (g2['osname'].isin(g3.osname) == False) & (g2['osname'].isin(g4.osname) == False)]
g6 = g3.append(g4)
g6 = g6.append(g5)

# update records in assets according to g6 data frame
print('update asset data for roads only')
for record in Asset:
    if '9c5d' in record['form_values']:
        print(''.join(record['form_values']['9c5d']['choice_values']), 'found')
        if ''.join(record['form_values']['2115']['choice_values']) in road:
            print('OS is part of the road')
            if any(x in ''.join(record['form_values']['9c5d']['choice_values']) for x in g6.osname) & any(
                            x in ''.join(record['status']) for x in
                            g6[(g6.osname == ''.join(record['form_values']['9c5d']['choice_values']))]['status']):
                print(g6[(g6.osname == ''.join(record['form_values']['9c5d']['choice_values']))]['osname'],
                      'already has status',
                      g6[(g6.osname == ''.join(record['form_values']['9c5d']['choice_values']))]['status'])
            else:
                if any(x in ''.join(record['form_values']['9c5d']['choice_values']) for x in g6.osname):
                    print(
                        (''.join(record['form_values']['9c5d']['choice_values']), "will change status from",
                         record['status']))
                    record['status'] = ''.join(
                        g6[(g6['osname'].str.contains(''.join(record['form_values']['9c5d']['choice_values'])))][
                            'status'])
                    print(('New status:', record['status']))
                    updatedRecord = fulcrum.records.update(record['id'], record)
                else:
                    if ''.join(record['status']) == 'Not inspected':
                        print('No change required')
                    else:
                        print(''.join(record['form_values']['9c5d']['choice_values']), 'is set to Not inspected')
                        record['status'] = 'Not inspected'
                        updatedRecord = fulcrum.records.update(record['id'], record)
        else:
            print('not a road')
    else:
        print('OS name field empty')

# new chunk to update assets for all other open spaces with a status change  to not inspected if older than 2 weeks
print('create data frame for IssueOs')
# IssueOs = fulcrum.records.search(url_params={'form_id': formIdIssue})['records']
# create new element for osname
for index in range(len(IssueOs)):
    if '9b3a' not in IssueOs[index]['form_values']:
        IssueOs[index]['osname'] = 'NA'
        IssueOs[index]['ostype'] = 'NA'
        logging.debug('No OS name field found')
    else:
        if IssueOs[index]['created_at'] >= str(osTimestamp):
            IssueOs[index]['osname'] = ''.join(IssueOs[index]['form_values']['9b3a'])
            IssueOs[index]['ostype'] = ''.join(IssueOs[index]['form_values']['e910']['choice_values'])
            logging.debug('OS name found and additional colums created')
        else:
            logging.debug('Record to old')
            IssueOs[index]['osname'] = 'NA'
            IssueOs[index]['ostype'] = 'NA'

IssueOs = pd.DataFrame(IssueOs)
# this just favorises the drama, 1 action required 2, approval requirec and 3 completion

IssueOs = IssueOs[(IssueOs.osname != 'NA')]
IssueOs = IssueOs[(IssueOs['ostype'].isin(os))]
# IssueOs['ostype'].unique()

IssueOs['osname'] = pd.core.strings.str_strip(IssueOs['osname'])
f = IssueOs.drop_duplicates(subset=['status', 'osname'])
f2 = f[['osname', 'status']]
f3 = f2[(f2.status == 'Action required')]
f4 = f2[(f2.status == 'Request for approval') & (f2['osname'].isin(f3.osname) == False)]
f5 = f2[
    (f2.status == 'Completed') & (f2['osname'].isin(f3.osname) == False) & (f2['osname'].isin(f4.osname) == False)]
f6 = f3.append(f4)
f6 = f6.append(f5)

# update records in assets according to f6 data frame

print('update asset data for OS only')
for record in Asset:
    if '9c5d' in record['form_values']:
        print(''.join(record['form_values']['9c5d']['choice_values']), 'found')
        if ''.join(record['form_values']['2115']['choice_values']) in os:
            print('OS is part of the road')
            if any(x in ''.join(record['form_values']['9c5d']['choice_values']) for x in f6.osname) & any(
                            x in ''.join(record['status']) for x in
                            f6[(f6.osname == ''.join(record['form_values']['9c5d']['choice_values']))]['status']):
                print(f6[(f6.osname == ''.join(record['form_values']['9c5d']['choice_values']))]['osname'],
                      'already has status',
                      f6[(f6.osname == ''.join(record['form_values']['9c5d']['choice_values']))]['status'])
            else:
                if any(x in ''.join(record['form_values']['9c5d']['choice_values']) for x in f6.osname):
                    print(
                        (''.join(record['form_values']['9c5d']['choice_values']), "will change status from",
                         record['status']))
                    record['status'] = ''.join(
                        f6[(f6['osname'].str.contains(''.join(record['form_values']['9c5d']['choice_values'])))][
                            'status'])
                    print(('New status:', record['status']))
                    updatedRecord = fulcrum.records.update(record['id'], record)
                else:
                    if ''.join(record['status']) == 'Not inspected':
                        print('No change required')
                    else:
                        print(''.join(record['form_values']['9c5d']['choice_values']), 'is set to Not inspected')
                        record['status'] = 'Not inspected'
                        updatedRecord = fulcrum.records.update(record['id'], record)
        else:
            print('not a os')
    else:
        print('OS name field empty')


# TODO: update readme
