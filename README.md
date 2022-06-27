# Pi in the Sky Example

## Broker

Run
```shell
docker run -it -p 1883:1883 -p 9001:9001 -v /ABSOLUTE/PATH/TO/broker/mosquitto.conf:/mosquitto/config/mosquitto.conf eclipse-mosquitto
```


## Backend

Install dependencies.
```shell
python -m pip install -r requirements.txt
```

Run application.
```shell
python main.py
```

## Frontend

Open `index.html` in a browser.


Hello