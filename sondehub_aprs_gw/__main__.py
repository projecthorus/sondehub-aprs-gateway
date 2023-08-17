import socket
socket.setdefaulttimeout(10)
import aprslib
import boto3
import os
import logging 
import sys
import urllib.request
import datetime
import pprint
import json
from collections import OrderedDict
from .comment_telemetry import extract_comment_telemetry

VERSION = "2023.07.30"

CALLSIGN = os.getenv("CALLSIGN")
SNS_PAYLOAD = os.getenv("SNS")
LISTENER_API = "https://api.v2.sondehub.org/amateur/listeners"
TIME_BETWEEN_LISTENER_UPDATES = 600 # 10 minutes
logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger("aprslib").setLevel(logging.INFO)
logging.getLogger("botocore").setLevel(logging.WARNING)
sns = boto3.client('sns')

positions = {}

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
BLOCKED_TOCALLS = (
    'APHAX', # # {'raw': 'SQ5AAG-11>APHAX0,TCPIP*,qAC,T2ROMANIA:@231308h5224.50N/02057.30EO180/000/A=000940 Clb=0m/s P=0hPa T=0oC U=0% ID=T1550189 [404.50MHz]', 'from': 'SQ5AAG-11', 'to': 'APHAX0', 'path': ['TCPIP*', 'qAC', 'T2ROMANIA'], 'via': 'T2ROMANIA', 'messagecapable': True, 'raw_timestamp': '231308h', 'timestamp': 1641769988, 'format': 'uncompressed', 'posambiguity': 0, 'symbol': 'O', 'symbol_table': '/', 'latitude': 52.40833333333333, 'longitude': 20.955, 'course': 180, 'speed': 0.0, 'altitude': 286.512, 'comment': 'Clb=0m/s P=0hPa T=0oC U=0% ID=T1550189 [404.50MHz]'}
    'APAT51', # Anytone AT-D578UV APRS mobile radio
    'APDR', # APRSDroid
    'APRARX', # Radiosonde Auto RX
    'OGFLR', # OGN Flarm Traffic (May need to add more tocalls here - refer https://github.com/glidernet/ogn-aprs-protocol/blob/master/aprsmsgs.txt )
)

# A list of 'from' calls, which we know are stations feeding in non-high-altitude-balloon traffic. 
BLOCKED_FROMCALLS = (
    'ON6DP-15', # Open Glider Network -> APRS-IS Gateway. Feeds in a lot of hot air balloons and gliders.
    'WIDE' # Corrupted packets due to bad iGates.
)

POSITIONS = {}

def isHam(thing):
    if "SONDEGATE" in thing["path"]: # {'raw': 'T1310753>APRARX,SONDEGATE,TCPIP,qAR,DF7OA-12:/233445h5242.24N/00959.93EO152/042/A=043155 Clb=3.7m/s t=-55.5C 405.701 MHz Type=RS41-SGP Radiosonde auto_rx v1.3.2 !w,%!', 'from': 'T1310753', 'to': 'APRARX', 'path': ['SONDEGATE', 'TCPIP', 'qAR', 'DF7OA-12'], 'via': 'DF7OA-12', 'messagecapable': False, 'raw_timestamp': '233445h', 'timestamp': 1641771285, 'format': 'uncompressed', 'posambiguity': 0, 'symbol': 'O', 'symbol_table': '/', 'latitude': 52.70402014652015, 'longitude': 9.99884065934066, 'course': 152, 'speed': 77.784, 'altitude': 13153.644, 'daodatumbyte': 'W', 'comment': 'Clb=3.7m/s t=-55.5C 405.701 MHz Type=RS41-SGP Radiosonde auto_rx v1.3.2'}
        return False

    if thing["to"].startswith(BLOCKED_TOCALLS): 
        return False

    if thing["from"].startswith(BLOCKED_FROMCALLS):
        return False

    if "comment" in thing:
        if "NSM is Not Sonde Monitor" in thing["comment"]: # {'raw': 'NSM20-11>APPMSP,F1ZWR-3*,WIDE2-2,qAR,F1ZNT-3:!4351.00N/00424.77EO169/023 Balloon is climbing   Ubatt 2.8V   NSM is Not Sonde Monitor', 'from': 'NSM20-11', 'to': 'APPMSP', 'path': ['F1ZWR-3*', 'WIDE2-2', 'qAR', 'F1ZNT-3'], 'via': 'F1ZNT-3', 'messagecapable': False, 'format': 'uncompressed', 'posambiguity': 0, 'symbol': 'O', 'symbol_table': '/', 'latitude': 43.85, 'longitude': 4.412833333333333, 'course': 169, 'speed': 42.596000000000004, 'comment': 'Balloon is climbing   Ubatt 2.8V   NSM is Not Sonde Monitor'}
            return False
        if "SondeID" in thing["comment"]: # Sonde monitor
            return False
        if "Ozonesonde" in thing["comment"]: 
            return False
        if "Recupero Radiosonde" in thing["comment"]: # "radiosonde recovery"
            return False
        if ("Weather Balloon" in thing["comment"]): # Turkish Radiosonde uploads, circa June 2023
            if thing["to"] == thing["from"]:
                return False


    # Default case. We have a position report with a balloon symbol, and it's passed the above checks,
    # so we consider it to be an amateur balloon. Filtering based on altitude will be handled in the tracker.
    return True

def post_listener(body):
    req = urllib.request.Request(LISTENER_API,method='PUT')
    req.add_header('Content-Type', 'application/json; charset=utf-8')
    jsondataasbytes = json.dumps(body).encode('utf-8')   # needs to be bytes
    req.add_header('Content-Length', len(jsondataasbytes))
    response = urllib.request.urlopen(req, jsondataasbytes)
    logging.debug(response)

def parser(x):
    try:
        thing = aprslib.parse(bytes(x))
    except (aprslib.exceptions.ParseError, aprslib.exceptions.UnknownFormat) as e:
        logging.debug(f"Error parsing APRS packet ({str(x)}): {str(e)}")
        return
    except Exception as e:
        logging.exception(f"Error parsing APRS packet ({str(x)})", exc_info=e)
        return

    # chase car
    if 'SHUB' in thing['path'] or 'SHUB1-1' in thing['path']:
        logging.info("Chase car:")
        logging.info(f"{thing}")
        try:
            payload = chase_aprs_to_sondehub(thing)
            if "comment" in thing:
                payload['comment'] = thing['comment']
            logging.info(f"payload: \n{pprint.pformat(payload)}\n")
        except Exception as e:
                logging.exception("Error converting to SondeHub payload type", exc_info=e)
                return
        try:
            post_listener(payload)
            logging.info(f"SNS published!")
        except:
            logging.exception("Error publishing to SNS topic")

    # balloons
    if thing["format"] != "object" and thing['symbol'] == 'O' and thing['symbol_table'] == "/":
        if isHam(thing):
            logging.info(f"{thing}")
            try:
                payload = aprs_to_sondehub(thing)
                logging.info(f"payload: \n{pprint.pformat(payload)}\n")
            except Exception as e:
                logging.exception("Error converting to SondeHub payload type", exc_info=e)
                return
            try:
                sns.publish(
                    TopicArn=SNS_PAYLOAD,
                    Message=json.dumps(payload)
                )
                logging.info(f"SNS published!")
            except:
                logging.exception("Error publishing to SNS topic")
            try: # try to publish listener information if required
                if payload["uploader_callsign"] in positions:
                    upload_listener(payload)
                else:
                    logging.info(f'No position info for {payload["uploader_callsign"]}!')
            except:
                logging.exception("Failed to update listener")
                return
        else:
            logging.debug(f"{thing}")

    try:
        positions[thing['from']] = {
            "latitude": thing["latitude"],
            "longitude": thing["longitude"],
            "altitude": thing["altitude"] if "altitude" in thing else 0,
            "comment": thing["comment"] if "comment" in thing else None,
            "last_sondehub_upload": None
        }
    except:
        logging.debug(f"Could not set location for position update")
        logging.debug(f"{thing}")

def upload_listener(payload):
    callsign = payload['uploader_callsign']
    position = positions[callsign]
    last_update = position['last_sondehub_upload'] 
    if last_update == None or(datetime.datetime.now() - last_update).seconds > TIME_BETWEEN_LISTENER_UPDATES:
        listener = {
            "software_name" : "SondeHub APRS-IS Gateway",
            "software_version": VERSION,
        
            "uploader_callsign": callsign,
            "uploader_position": [
                position["latitude"],
                position["longitude"],
                position["altitude"]
            ],
            "mobile": False
        }
        if position['comment']:
            listener['uploader_radio'] = position['comment']
        post_listener(listener)
        logging.info(listener)
        logging.info(f"Listener SNS published!")
        positions[callsign]["last_sondehub_upload"] = datetime.datetime.now()


def aprs_to_sondehub(thing):
    # use cached time stamp if none provided
    if "timestamp" not in thing or thing['timestamp'] == 0:
        non_path_raw = thing['raw'].split(":",1)[1]
        if non_path_raw in rx_times:
            thing_datetime = rx_times[non_path_raw]
        else:
            thing_datetime = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            rx_times[non_path_raw] = thing_datetime
            if len(rx_times) > 100000:
                rx_times.popitem(last=False)
    else:
        thing_datetime = datetime.datetime.fromtimestamp(thing["timestamp"], datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    
    payload = {
        "software_name" : "SondeHub APRS-IS Gateway",
        "software_version": VERSION,
        "uploader_callsign": thing["path"][-1],
        "path": ",".join(thing["path"]),
        "time_received": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "payload_callsign": thing["from"],
        "datetime": thing_datetime,
        "lat": thing["latitude"],
        "lon": thing["longitude"],
        "alt": thing["altitude"],
        "comment": thing["comment"] if "comment" in thing  else None,
        "raw": thing["raw"],
        "aprs_tocall": thing["to"],
        "modulation": "APRS"
    }

    # Attempt to extract any comment-field telemetry
    payload.update(extract_comment_telemetry(payload))

    return payload

def chase_aprs_to_sondehub(thing):
    payload = {
        "software_name" : "SondeHub APRS-IS Gateway",
        "software_version": VERSION,

        "uploader_callsign": thing['from'],
        "path": ",".join(thing["path"]),
        "uploader_position": [
            thing["latitude"],
            thing["longitude"],
            thing["altitude"] if "altitude" in thing else 0
        ],
        "uploader_radio": thing["comment"] if "comment" in thing else None,
        "raw": thing["raw"],
        "aprs_tocall": thing["to"],
        "mobile": True
    }

    return payload
while 1:
    AIS = aprslib.IS(CALLSIGN,aprslib.passcode(CALLSIGN), port=14580)
    AIS.set_filter("t/p")
    AIS.connect()

    AIS.consumer(callback=parser, raw=True)