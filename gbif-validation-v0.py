# imports
import logging, json, math
import time
from datetime import datetime, timedelta

from fulcrum import Fulcrum
from pygbif import species

# fulcrum vars BPLA
with open("/credentials.json") as c:
	credentials = json.load(c)

fulcrum = Fulcrum(key=credentials['fulcrum_api'])
formID = credentials['form_id']
logging.basicConfig(filename='gbifupdate.log', level=logging.INFO)
weektimestamp = datetime.today() - timedelta(days=7)  # number of days as a delimiter
monthtimestamp = datetime.today() - timedelta(days=30)  # number of days as a delimiter
weeknumber = time.strftime("%U")
today = datetime.today()

# get records
formData = fulcrum.forms.find(credentials['TMO_TI_form'])

recordCount = formData['form']['record_count']
pages = math.ceil(recordCount / 5000)
# way cleaner than my script. Thanks!
data = []
for p in range(1, pages + 1):
    dataPage = fulcrum.records.search(
        url_params={'form_id': credentials['TMO_TI_form'], 'page': p, 'per_page': 5000})['records']
    data.extend(dataPage)

count = 0
for record in data:
    if len(record['form_values']['c0ad']['choice_values']) == 0:
        fulcrumSpecies = str(''.join(record['form_values']['c0ad']['other_values']))
    else:
        fulcrumSpecies = str(''.join(record['form_values']['c0ad']['choice_values']))

    fulcrumSpecies = fulcrumSpecies.replace(" sp.", "")

    print('fulcrum species cleaned (sp. removed):', fulcrumSpecies)

    if str('14eb') in record['form_values'] and str(fulcrumSpecies) in record['form_values']['14eb']:
        print('GBIF species matches fulcrum species. No update required. Jumping to next.')
    else:
        unknown = ["Unknown", "ID later"]
        if ''.join(fulcrumSpecies) in unknown:
            print('fulcrumSpecies is unknown or set to ID later')
            record['form_values']['a604'] = str("Unknown")
            record['form_values']['80e2'] = str("Unknown")
            record['form_values']['14eb'] = str("Unknown")
            record['form_values']['9d3a'] = str("Unknown")
            record['form_values']['7022'] = str("Unknown")
            recordUpdated = fulcrum.records.update(record['id'], record)
            count = count + 1
            print(fulcrumSpecies)
            print(record['form_values']['14eb'])
            print(count)
        else:
            gbifSpecies = species.name_lookup(q=fulcrumSpecies)
            gbifcount = gbifSpecies['count']
            print('fulcrum species found in gbif. Number of results for name match:', gbifcount, fulcrumSpecies)
            # print(gbifSpecies['results'][0]['canonicalName'])
            # data = ['rank', 'class', 'canonicalName', 'synonym', 'taxonomicStatus']
            if gbifSpecies['count'] > 0:
                rank = []
                for i in gbifSpecies['results']:
                    my_dict = {}
                    my_dict = i.get('rank')
                    rank.append(my_dict)
                classg = []
                for i in gbifSpecies['results']:
                    my_dict = {}
                    my_dict = i.get('class')
                    classg.append(my_dict)
                canonicalName = []
                for i in gbifSpecies['results']:
                    my_dict = {}
                    my_dict = i.get('canonicalName')
                    canonicalName.append(my_dict)
                synonym = []
                for i in gbifSpecies['results']:
                    my_dict = {}
                    my_dict = i.get('synonym')
                    synonym.append(my_dict)
                taxonomicStatus = []
                for i in gbifSpecies['results']:
                    my_dict = {}
                    my_dict = i.get('taxonomicStatus')
                    taxonomicStatus.append(my_dict)
                record['form_values']['a604'] = str(rank[0])
                record['form_values']['80e2'] = str(classg[0])
                record['form_values']['14eb'] = str(canonicalName[0])
                record['form_values']['9d3a'] = str(synonym[0])
                record['form_values']['7022'] = str(taxonomicStatus[0])
                recordUpdated = fulcrum.records.update(record['id'], record)
                count = count + 1
                print(fulcrumSpecies)
                print(record['form_values']['14eb'])
                print(count)
                # prevSpecies = fulcrumSpecies
            else:
                print('gbif species did not return any results.')
                record['form_values']['a604'] = str("Unknown")
                record['form_values']['80e2'] = str("Unknown")
                record['form_values']['14eb'] = str("Unknown")
                record['form_values']['9d3a'] = str("Unknown")
                record['form_values']['7022'] = str("Unknown")
                recordUpdated = fulcrum.records.update(record['id'], record)
                count = count + 1
                print(fulcrumSpecies)
                print(record['form_values']['14eb'])
                print(count)


logging.info('%s records updated on %s', count, str(datetime.today()))

