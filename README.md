# AutoID-server
This repo is used for the experiment demand of Project AutoID, a pervasive computing solution with RFID. The main mission for this module is about interaction with RFID reader and MongoDB.

## Usage
```bash
docker build -t autoid_server .
docker run -it --rm --name autoid_running autoid_server 
```