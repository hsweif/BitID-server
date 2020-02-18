# AutoID-server

This repo is used for the experiment demand of Project AutoID, a pervasive computing solution with RFID. The main mission for this module is about interaction with RFID reader and MongoDB.

## Usage

### Installation

After cloning the repo, you will need to initialize the submodule.

```bash
git submodule init
git submodule update
```

For Python dependencies, it is recommended to run this repo with a Python3 virtualenv with pip. You can install the dependencies with:

```bash
pip install -r requirements.txt
```

### Run

Simply use below command to run the server in localhost:8000

```bash
python3 server.py
```

### Database management

We also provide simple command line interface to interact with MongoDB.
You can delete an object from the database or add toggle control to the database with:

```bash
python3 DatabaseHandler.py --mode delete
python3 DatabaseHandler.py --mode toggle
```

Further instructions can be found in the interactive environment.

You can choose to store the raw data into MongoDB with:

```bash
python3 server.py -s
```

On the other hand, if you want to get data in a specific range from mongodb. We provided a method in Databasehandler. Use as:

```python
TYPE = util.OBJECT # or util.TAG | util.RAW | util.RECG
result = db.mongoHandler.getMongoData(TYPE, start_time, end_time)
# start_time, end_time are datetime object
# you can get a list of documents in this time range in result.
```

You can see DatabaseHandler.py's main function for more detailed usage.

## Dependencies

If you want to use local python environment or face difficulties in using requirements. Make sure your interpreter contains packages listed in `requirements.txt`.
Besides, we use MongoDB to store the data. Therefore please be sure you installed mongodb or accessed to the remote one.
Both MongoDB and reader's settings could be modified in `config.json`.

**Please run the MongoDB on the port you assigned in `config.json` to store the records.**