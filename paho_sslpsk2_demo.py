"""
`paho mqtt client` using `TSL-PSK` communication.
**This is a work in process, not yet functional.**

Expected result:
The client will connect to a MQTT broker subscribing to the `$SYS/#` topic
printing on the terminal every message received.

The broker tested is a `Mosquitto 2.0.14`running in a docker container from
the official https://hub.docker.com/_/eclipse-mosquitto with the tag
`2.0.14-openssl`

The `psk` for `mosquitto` has this content:
1234:1234

Check more details about the environment on the README.md of the repository
https://github.com/maovidal/paho_sslpsk2_demo 
"""


import ssl
import paho.mqtt.client as mqtt
from sslpsk2.sslpsk2 import _ssl_set_psk_server_callback, _ssl_set_psk_client_callback


# Some definitions to be modified according to your setup:
CONFIG_MQTT_BROKER='broker.local'
CONFIG_MQTT_BROKER_PORT=8883
CONFIG_CLIENT_ID='paho_sslpsk2' # Having a fixed ID may help debugging on the broker


# Modify SSLContext to use sslpsk2
# https://github.com/drbild/sslpsk/issues/19#issue-547462099

def _ssl_setup_psk_callbacks(sslobj):
    psk = sslobj.context.psk
    hint = sslobj.context.hint
    identity = sslobj.context.identity
    if psk:
        if sslobj.server_side:
            cb = psk if callable(psk) else lambda _identity: psk
            _ssl_set_psk_server_callback(sslobj, cb, hint)
        else:
            cb = psk if callable(psk) else lambda _hint: psk if isinstance(psk, tuple) else (psk, identity)
            _ssl_set_psk_client_callback(sslobj, cb)


class SSLPSKContext(ssl.SSLContext):
    @property
    def psk(self):
        return getattr(self, "_psk", None)

    @psk.setter
    def psk(self, psk):
        self._psk = psk

    @property
    def hint(self):
        return getattr(self, "_hint", None)

    @hint.setter
    def hint(self, hint):
        self._hint = hint

    @property
    def identity(self):
        return getattr(self, "_identity", None)

    @identity.setter
    def identity(self, identity):
        self._identity = identity


class SSLPSKObject(ssl.SSLObject):
    def do_handshake(self, *args, **kwargs):
        _ssl_setup_psk_callbacks(self)
        super().do_handshake(*args, **kwargs)


class SSLPSKSocket(ssl.SSLSocket):
    def do_handshake(self, *args, **kwargs):
        _ssl_setup_psk_callbacks(self)
        super().do_handshake(*args, **kwargs)


SSLPSKContext.sslobject_class = SSLPSKObject
SSLPSKContext.sslsocket_class = SSLPSKSocket


# Preparations to use the new SSLPSKContext object with Paho
# https://github.com/eclipse/paho.mqtt.python/issues/451#issuecomment-705623084

context = SSLPSKContext(ssl.PROTOCOL_TLS)
context.set_ciphers('PSK')
context.psk = bytes.fromhex('1234')
context.identity = b'username'

# Paho preparations according to the official guide
# https://github.com/eclipse/paho.mqtt.python#getting-started

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

client = mqtt.Client(
    client_id=CONFIG_CLIENT_ID,
)
client.tls_set_context(context)  # Here we apply the new `SSLPSKContext``
client.on_connect = on_connect
client.on_message = on_message

def main():
    client.connect(
        host=CONFIG_MQTT_BROKER,
        port=CONFIG_MQTT_BROKER_PORT,
    )
    client.loop_forever()


if __name__ == '__main__':
    main()
