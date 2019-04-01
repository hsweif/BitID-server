# AutoID-server
This repo is used for the experiment demand of Project AutoID, a pervasive computing solution with RFID. The main mission for this module is about interaction with RFID reader and MongoDB.

## Usage
It is recommended to run this repo with a Python3 virtualenv. You can install the dependencies with:
```bash
pip3 install -r requirements.txt
```
Simply use below command to run the server in localhost:8000
```bash
python3 server.py
```

You can choose to store the raw data into MongoDB with:
```bash
python3 server.py -s
```

## Dependencies
If you want to use local python environment or face difficulties in using requirements. Make sure your interpreter contains packages below.
Suppose you use pip to manage your packages, run these commands.
```bash
pip3 install flask
pip3 install pandas
pip3 install numpy
```
Besides, we use MongoDB to store the data. Therefore please be sure you installed mongodb or accessed to the remote one.
Both MongoDB and reader's settings could be modified in `config.json`.