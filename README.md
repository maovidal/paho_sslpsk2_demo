`paho mqtt client` using `TSL-PSK` communication.

**This is a work in process, not yet functional.**


# Expected result


The client will connect to a MQTT broker subscribing to the `$SYS/#` topic printing on the terminal every message received.


# Preparations


## MQTT Broker

The broker tested is a `Mosquitto 2.0.14`running in a docker container from the official https://hub.docker.com/_/eclipse-mosquitto with the tag `2.0.14-openssl`.

The `psk` for `mosquitto` has this content:
1234:1234

Before going any further, it should help to confirm the Broker is working as expected to use `PSK`. One way to do it, having a machine with the official `mosquitto_pub` and `mosquitto_sub` clients with access to the `broker`(named here `broker.local`), is to issue each of the following on their own terminals:

```
mosquitto_sub --psk-identity 1234 --psk 1234 -h broker.local -p 8883 -t TestTopic -i TheReceiver
```

```
mosquitto_pub --psk-identity 1234 --psk 1234 -h broker.local -p 8883 -t TestTopic -m Hello -i TheSender
```

On each of the latter, the former should display 'Hello`.


## The machine running the Python script


`PSK` ciphers should be available to the Python environment running the script (See https://github.com/eclipse/paho.mqtt.python/issues/451#issuecomment-705682414). In my case, it was quite tricky to achieve that. For some reason my environment had available a very old `OpenSSL` with no `PSK` support.

On a `Intel macOS 12.5` this was resolved installing `openssl@3` via `brew` and making sure to follow `brew` indications about making available `openssl` when issuing `brew link openssl --force`.

Regarding `sspsk2` I manages to install it ussing `ARCHFLAGS="-arch x86_64" pip3 install sslpsk2` otherwise `pip` complained about an unsupported achitecture.


# Usage


run the script [paho_sslpsk2_demo.py](paho_sslpsk2_demo.py)

