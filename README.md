# py-fulcrum-tools

Tools for interacting with the fulcrum app API using python. See http://www.fulcrumapp.com/developers/api/ for more info on the Fulcrum API.

## Tools

* `change-record-status.py` - update the status of every record that is older than X days. This is ment to be scheduled outside pyhton using cronjobs.

## Setup

Copy `change-record-status.py` to `change-record-status.py`, fill in your API token, and populate the form and creator UUID dictionaries.

## Usage

### 1. Copy `change-record-status.py`

