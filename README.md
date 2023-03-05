This repository demonstrates how to set a MQTT client based on `paho mqtt client` to use `SSL PSK` communication for the MQTT protocol based on the discussion and resources provided by the post https://github.com/eclipse/paho.mqtt.python/issues/451


# Current status

- It is tested working on Linux, Python 3.10 and 3.11.
- It is not working on macOS with OpenSSL@3. Please [see below](#the-macos-case).


# Expected result


The client will connect to a MQTT broker subscribing to the `#` topic printing on the terminal every message received.


# Preparations


## MQTT Broker

The broker tested is a `Mosquitto 2.0.15`running in a docker container from the official https://hub.docker.com/_/eclipse-mosquitto with the tag `2.0.15-openssl`. Its name on the network is `broker.local`

The `psk` file for `mosquitto` has this content:
>hello:1234


## The machine running the Python script


`PSK` ciphers should be available to the Python environment running the script. A quick check could be performed issuing this on the shell of the machine considering the above stated credentials:

```
openssl s_client -psk 1234 -psk_identity hello -connect broker.local:8883
```

Also, the `sspsk2` package from https://github.com/autinerd/sslpsk2/ should be installed on the machine.


# Usage


Just run the script [paho_sslpsk2_demo.py](paho_sslpsk2_demo.py). The payload published by another client should be printed by the script.


# Troubleshooting


The official `mosquitto_pub` and `mosquitto_sub` clients can be used on the remote machine to check its ability to connect to the `broker`. This will check that the broker, its configuration, and clients with proven apps are able to work together using `PSK`. 

A client can subscribe to the topic `TestTopic`:

```
mosquitto_sub --psk-identity hello --psk 1234 -h broker.local -p 8883 -t TestTopic -i TheReceiver
```

Another client can publish a `Hello` string to that `TestTopic`:

```
mosquitto_pub --psk-identity hello --psk 1234 -h broker.local -p 8883 -t TestTopic -m Hello -i TheSender
```


## Check the Mosquitto Broker

The `psk` file above mentioned should contain the identity and key expected and the broker configuration file should contain matching port and location for that psk file:

```
listener 8883
psk_file /mosquitto/config/psk
```


## The macOS case

I haven't been able to get a working `paho` client working. **Any help regarding how to solve the macOS case will be greatly appreciated.**

While the test of the combo `mosquitto_sub`/`mosquitto_pub` works on a `Intel macOS 13.2.1` with `openssl@3` installed via `brew`, testing the script of this repo reports:

```
ssl.SSLError: [SSL: SSLV3_ALERT_HANDSHAKE_FAILURE] sslv3 alert handshake failure (_ssl.c:997)
```

It may be worth to mention that it was quite tricky for me to install the OpenSSL on the Mac machine. Those are my notes:

- Make sure to follow `brew` indications about making available `openssl` when issuing `brew link openssl --force` as macOS provides LibreSSL.
- I managed to install `sspsk2` using `ARCHFLAGS="-arch x86_64" pip3 install sslpsk2`. Otherwise `pip` complains about an unsupported architecture.
