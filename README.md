This repository demonstrates how to set a MQTT client based on `paho mqtt client` to use `SSL PSK` communication for the MQTT protocol based on the discussion and resources provided by the post https://github.com/eclipse/paho.mqtt.python/issues/451


# Current status

- It is tested working on Linux, Python 3.10 and 3.11.
- It is tested working on macOS 3.11.3, with Python compiled to use OpenSSL. Please [see below](#the-macos-case).
- It does not work on Rocky Linux 8 with python 3.6 [Reported with #4 by @pat1](https://github.com/maovidal/paho_sslpsk2_demo/issues/4).


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

I was not able to get `sslpsk2` running on a macOS using the official Python installer. I presume that the reason is that this OS uses `LibreSSL` instead `OpenSSL`.

With the official Python for macOS, testing the combo `mosquitto_sub`/`mosquitto_pub` on a `Intel macOS 13.2.1` it reported:

```
ssl.SSLError: [SSL: SSLV3_ALERT_HANDSHAKE_FAILURE] sslv3 alert handshake failure (_ssl.c:997)
```

The above does not happen if `Python` is installed via `brew`. Check its official formulae: https://docs.brew.sh/Homebrew-and-Python#python-3y

### Tips about installing `sslpsk2`:

- Once `pip` complained about an unsupported architecture. I managed to install `sslpsk2` using `ARCHFLAGS="-arch x86_64" pip3 install sslpsk2`. 
- Once I got this error when issuing `pip install sslpsk2`:

```
`clang: error: invalid version number in 'MACOSX_DEPLOYMENT_TARGET=13'`
```

Check this post https://stackoverflow.com/a/64838849/15786299 where it mentions that it can be solved with:

```
sudo rm -rf /Library/Developer/CommandLineTools
sudo xcode-select --install
```
