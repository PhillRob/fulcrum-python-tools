# py-fulcrum-tools

Tools for interacting with the fulcrum app API using python. See http://developer.fulcrumapp.com/api/intro/ for more info on the Fulcrum API. [Requests](http://docs.python-requests.org/en/latest/) takes care of our HTTP chatting, and is automatically installed when using the steps above.

## Tools

* ```python
change-record-status.py``` - update the status of every record that is older than X days. This is ment to be scheduled outside pyhton using crontab.

## Setup

Run `pip install fulcrum` to install the fulcrum python library 
Copy `change-record-status.py` to `change-record-status.py` and edit your `formId`, `apiToken`,`newlabel` and `days`in `change-record-status.py` to suit you. You may change the field that is being update as well.

## Usage

* 1. Copy `change-record-status.py` into your onto you linux machine
* 2. Do `crontab -e` and add the path of the script and the frequency eg `minute hour day-of-month month day-of-week /path/to/change-record-status.py`


