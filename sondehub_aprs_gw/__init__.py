import socket
socket.setdefaulttimeout(10)
import aprs
import aprslib
import boto3
import os
import logging 
import sys
import datetime
import pprint
import json
from collections import OrderedDict

CALLSIGN = os.getenv("CALLSIGN")
SNS = os.getenv("SNS")
logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger("aprslib").setLevel(logging.INFO)
logging.getLogger("botocore").setLevel(logging.WARNING)
sns = boto3.client('sns')

rx_times = OrderedDict()

class CustomFormatter(logging.Formatter):

    grey = "\x1b[2m"
    green = "\x1b[32;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: green + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

ch.setFormatter(CustomFormatter())

logging.getLogger().addHandler(ch)

# A list of tocalls which we know are from devices that are either pushing radiosonde packets,
# or are from devices which are very unlikely to be on a balloon (e.g. mobile radios)
BLOCKED_TOCALLS = [
    'APHAX0', # # {'raw': 'SQ5AAG-11>APHAX0,TCPIP*,qAC,T2ROMANIA:@231308h5224.50N/02057.30EO180/000/A=000940 Clb=0m/s P=0hPa T=0oC U=0% ID=T1550189 [404.50MHz]', 'from': 'SQ5AAG-11', 'to': 'APHAX0', 'path': ['TCPIP*', 'qAC', 'T2ROMANIA'], 'via': 'T2ROMANIA', 'messagecapable': True, 'raw_timestamp': '231308h', 'timestamp': 1641769988, 'format': 'uncompressed', 'posambiguity': 0, 'symbol': 'O', 'symbol_table': '/', 'latitude': 52.40833333333333, 'longitude': 20.955, 'course': 180, 'speed': 0.0, 'altitude': 286.512, 'comment': 'Clb=0m/s P=0hPa T=0oC U=0% ID=T1550189 [404.50MHz]'}
    'APAT51-1', # Anytone AT-D578UV APRS mobile radio
]

def isHam(thing):
    if "SONDEGATE" in thing["path"]: # {'raw': 'T1310753>APRARX,SONDEGATE,TCPIP,qAR,DF7OA-12:/233445h5242.24N/00959.93EO152/042/A=043155 Clb=3.7m/s t=-55.5C 405.701 MHz Type=RS41-SGP Radiosonde auto_rx v1.3.2 !w,%!', 'from': 'T1310753', 'to': 'APRARX', 'path': ['SONDEGATE', 'TCPIP', 'qAR', 'DF7OA-12'], 'via': 'DF7OA-12', 'messagecapable': False, 'raw_timestamp': '233445h', 'timestamp': 1641771285, 'format': 'uncompressed', 'posambiguity': 0, 'symbol': 'O', 'symbol_table': '/', 'latitude': 52.70402014652015, 'longitude': 9.99884065934066, 'course': 152, 'speed': 77.784, 'altitude': 13153.644, 'daodatumbyte': 'W', 'comment': 'Clb=3.7m/s t=-55.5C 405.701 MHz Type=RS41-SGP Radiosonde auto_rx v1.3.2'}
        return False
    if thing["to"] in BLOCKED_TOCALLS: 
        return False
    if "NSM is Not Sonde Monitor" in thing["comment"]: # {'raw': 'NSM20-11>APPMSP,F1ZWR-3*,WIDE2-2,qAR,F1ZNT-3:!4351.00N/00424.77EO169/023 Balloon is climbing   Ubatt 2.8V   NSM is Not Sonde Monitor', 'from': 'NSM20-11', 'to': 'APPMSP', 'path': ['F1ZWR-3*', 'WIDE2-2', 'qAR', 'F1ZNT-3'], 'via': 'F1ZNT-3', 'messagecapable': False, 'format': 'uncompressed', 'posambiguity': 0, 'symbol': 'O', 'symbol_table': '/', 'latitude': 43.85, 'longitude': 4.412833333333333, 'course': 169, 'speed': 42.596000000000004, 'comment': 'Balloon is climbing   Ubatt 2.8V   NSM is Not Sonde Monitor'}
        return False
    if "Sonde" in thing["comment"]: # Generic filter for radiosonde packets. This may result in some false-positives.
        return False
    if "sonde" in thing["comment"]: # Generic filter for radiosonde packets. This may result in some false-positives.
        return False
    return True

def parser(x):
    thing = aprslib.parse(bytes(x))
    if thing["format"] != "object":
        if isHam(thing):
            logging.info(f"{thing}")
            try:
                payload = aprs_to_sondehub(thing)
                logging.info(f"payload: \n{pprint.pformat(payload)}\n")
            except:
                logging.exception("Error converting to SondeHub payload type")
            try:
                sns.publish(
                    TopicArn=SNS,
                    Message=json.dumps(payload)
                )
                logging.info(f"SNS published!")
            except:
                logging.exception("Error publishing to SNS topic")
        else:
            logging.debug(f"{thing}")

def aprs_to_sondehub(thing):
    # use cached time stamp if none provided
    if "timestamp" not in thing or thing['timestamp'] == 0:
        non_path_raw = thing['raw'].split(":",1)[1]
        if non_path_raw in rx_times:
            thing_datetime = rx_times[non_path_raw]
        else:
            thing_datetime = datetime.datetime.utcnow().isoformat() + "Z"
            rx_times[non_path_raw] = thing_datetime
            if len(rx_times) > 100000:
                rx_times.popitem(last=False)
    else:
        thing_datetime = datetime.datetime.fromtimestamp(thing["timestamp"], datetime.timezone.utc).isoformat() + "Z"
    
    payload = {
        "software_name" : "aprs",
        "software_version": thing["to"],
        "uploader_callsign": thing["path"][-1],
        "path": ",".join(thing["path"]),
        "time_received": datetime.datetime.utcnow().isoformat() + "Z",
        "payload_callsign": thing["from"],
        "datetime": thing_datetime,
        "lat": thing["latitude"],
        "lon": thing["longitude"],
        "alt": thing["altitude"],
        "comment": thing["comment"] if "comment" in thing  else None,
        "raw": thing["raw"],
        "modulation": "APRS"
    }
    return payload

a = aprs.TCP(CALLSIGN.encode(), str(aprslib.passcode(CALLSIGN)).encode(), aprs_filter="s/O//".encode()) # filter position and balloon
a.start()

a.interface.settimeout(None)
a.receive(callback=parser)