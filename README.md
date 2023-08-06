# Fulcrum Python Tools

Tools for interacting with the fulcrum app API using python. See http://developer.fulcrumapp.com/api/intro/ for more info on the Fulcrum API. [Requests](http://docs.python-requests.org/en/latest/) takes care of our HTTP chatting, and is automatically installed when using the steps below.

## Tools

* `change-record-status.ipynb` - Update the status of every record that is older than 12 `days`.
* [`deleteRecords.py`](https://github.com/timstallmann/py-fulcrum-tools/blob/master/deleteRecords.py) - Bulk delete records belonging to a particular changeset. 
* `archive-complete-issue.py` changes the record's status based on the time delta between today and the last update date.
* ~~`count-drives-record-status.py`- The records status is updated based on the records status of a 2nd app. It was intended to show the condition of parks and garden based on the number of complaints recieved.~~ 
* `fulcrum-mailer.py`- Shows count data of records over a time and according to status. Intended as an informal activity summary for management. 
* `more-2-come`

## Setup

* Run `pip install fulcrum` to install the fulcrum python library.
* Copy the `py`-file into your onto you linux machine and edit your `formId`, credentials and `days`. 

## Usage

* Do `crontab -e` and add the path of the script and the frequency eg `minute hour day-of-month month day-of-week /path/to/my-file.py`


