# Pi in the Sky Example

## Broker

The broker runs in a [Docker](https://www.docker.com/products/personal/) container. You may have to authorize file sharing to the `broker/` directory.

From the `broker/` directory, run it via a shell (terminal or command prompt) command:
```shell
docker run -it -p 1883:1883 -p 9001:9001 -v /ABSOLUTE/PATH/TO/broker/mosquitto.conf:/mosquitto/config/mosquitto.conf eclipse-mosquitto
```
replacing `/ABSOLUTE/PATH/TO` with the absolute path to your project directory. On Windows, start with the drive letter, e.g., `C:/PATH/TO`, and on Mac/Linux include the root, e.g., `/PATH/TO`.


## Backend

The backend relies on the `paho-mqtt` library. From the `backend/` directory, install dependencies by running the shell (terminal or command prompt) command:
```shell
python -m pip install -r requirements.txt
```
and run the backend application with the shell (terminal or command prompt) command:
```shell
python main.py
```

## Frontend

From the `frontend/` directory, open `index.html` in a browser.