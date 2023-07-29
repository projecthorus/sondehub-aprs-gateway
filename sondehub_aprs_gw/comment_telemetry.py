#
#   SondeHub APRS Gateway - Comment-Field Telemetry Extractor
#
#   Mark Jessop <vk5qi@rfhead.net>
#
import logging
import re

# APRS tocalls (device IDs) of trackers which are known to send comment-field
# telemetry with satellite information reported as 'Sn' or 'Sats=0', and commonly send 
# positions with no GNSS lock ('S0', 'Sats=0')
APRS_S0_TRACKERS = ['APZQAP', 'APBCRS', 'APZQVA']

def extract_comment_telemetry(payload):
    """
    Attempts to determine what kind of APRS tracker is in use,
    then attempts to extract telemetry from the comment field.

    Takes the payload data to be sent to sondehub as an input, and
    returns a dictionary with any keys to be added or overwritten. 
    """

    try:
        if payload['comment'] is None:
            # No Comment data, return.
            return {}

        # Detect StratoTrack telemtry via ',StrTrk' in the comment field.
        if payload['comment'].startswith(',StrTrk'):
            return extract_stratotrack_telemetry(payload)

        # Detect WB8ELK Skytracker by the toCall
        if payload['aprs_tocall'].startswith('APELK0'):
            return extract_wb8elk_skytracker_telemetry(payload)

        # LightAPRS
        if payload['aprs_tocall'] == 'APLIGA':
            return extract_lightaprs_telemetry(payload)

        # RS41ng
        if payload['aprs_tocall'] == 'APZ41N':
            return extract_RS41ng_telemetry(payload)

        # Detect trackers that are known to send positions with no
        # GNSS lock, and report this in the comment field as 'S0'
        if payload['aprs_tocall'] in APRS_S0_TRACKERS:
            return extract_aprs_s0_telemetry(payload)



    except Exception as e:
        logging.exception("Failed extracting comment telemetry")

    # Default case is to return nothing.
    return {}



def extract_stratotrack_telemetry(payload):
    """
    Attempt to extract telemetry from a StratoTrack APRS comment field.
    Example: ",StrTrk,84,9,1.46V,-14C,2127Pa,"
    Link: https://www.highaltitudescience.com/products/stratotrack-aprs-transmitter
    """

    try:
        output = {'model': 'StratoTrack'}

        # Comma-delimited fields.
        _fields = payload['comment'].split(',')
        # Extract each field.
        output['frame'] = int(_fields[2])
        output['sats'] = int(_fields[3])
        # Only extract the following fields if we detect the exact units we expect.
        if _fields[4].endswith('V'):
            output['batt'] = float(_fields[4][:-1])
        if _fields[5].endswith('C'):
            output['temp'] = float(_fields[5][:-1])
        if _fields[6].endswith('Pa'):
            output['ext_pressure'] = float(_fields[6][:-2])/100.0

        return output
    except Exception as e:
        logging.exception("Error extracting telemetry from StratoTrack")


    return {}


def extract_wb8elk_skytracker_telemetry(payload):
    """
    Attempt to extract telemetry from a WB8ELK SkyTracker APRS comment field.
    Example: "12 4.34 33 1991 101"
    Link: https://gmigliarini.wixsite.com/wb8elk
    """
    try:
        output = {'model': 'WB8ELK SkyTracker'}

        # Space-delimited fields, but use split with no argument in case of more than one space
        _fields = payload['comment'].split()

        # Only extract data if we have the exact number of expected fields.
        if len(_fields) == 5:
            output['sats'] = int(_fields[0])
            output['solar_panel'] = float(_fields[1])
            output['temp'] = float(_fields[2])
            # Field 3 is altitude in metres, so no need to extract this.
            output['frame'] = int(_fields[4])

        return output
    except Exception as e:
        logging.exception("Error extracting telemetry from WB8ELK SkyTracker")

    return {}


def extract_lightaprs_telemetry(payload):
    """
    Attempt to extract telemetry from a LightAPRS tracker comment field.
    Example: 015TxC 29.00C 1019.86hPa 4.59V 06S
    Link: https://github.com/lightaprs/LightAPRS-W-1.0/blob/master/LightAPRS-W-pico-balloon/LightAPRS-W-pico-balloon.ino#L497
    """

    try:
        output = {'model': 'LightAPRS'}

        # Space delimited fields, but sometimes with more than one space.
        _fields = payload['comment'].split()

        print(_fields)
        # Explicitly check for the expected suffix on every field.
        if _fields[0].endswith('TxC'):
            output['frame'] = int(_fields[0][:-3])
        
        if _fields[1].endswith('C'):
            output['temp'] = float(_fields[1][:-1])

        if _fields[2].endswith('hPa'):
            output['ext_pressure'] = float(_fields[2][:-3])

        if _fields[3].endswith('V'):
            output['batt'] = float(_fields[3][:-1])

        if _fields[4].endswith('S'):
            output['sats'] = int(_fields[4][:-1])

        return output

    except Exception as e:
        logging.exception("Error extracting telemetry from LightAPRS Tracker")

    return {}


def extract_RS41ng_telemetry(payload):
    """
    Attempt to extract telemetry from a RS41ng tracker comment field.
    Example: P6S7T29V2947C00 JO00WW - RS41ng radiosonde Toto test
    Link: https://github.com/mikaelnousiainen/RS41ng
    """

    try:
        output = {'model': 'RS41ng'}

        # Split comment field, telemetry should be the first
        _fields = payload['comment'].split()

        # Extract telemetry segments
        pattern = r'([A-Z])(\d+)'
        _matches = re.findall(pattern, _fields[0])

        # Iterate through the found matches, and look for specific identifiers
        for _telem in _matches:
            _type = _telem[0]
            _data = _telem[1]

            if _type == 'P':
                output['frame'] = int(_data)
            elif _type == 'S':
                output['sats'] = int(_data)
            elif _type == 'T':
                output['temp'] = int(_data)
            elif _type == 'V':
                output['batt'] = int(_data)/1000.0

        return output

    except Exception as e:
        logging.exception("Error extracting telemetry from RS41ng telemetry")

    return {}


def extract_aprs_s0_telemetry(payload):
    """
    Special case for a set of APRS tracker firmware (seems to be mainly for RS41s)
    that transmit telemtry information in the comment field in the form:

    P9/S7/T27/V283/ 06:40:52/EV/BT31.2°C
    or
    P58S0T33V3975C00

    where 'S0' indicates no GNSS lock, yet the tracker still beacons invalid
    positions.

    There are also trackers which report no sats as 'Sats=0' or 'Sat=0'

    To handle this, we add telemetry indicating the lack of GNSS lock, which
    can be filtered on the tracker.

    Examples of firmware that do this:
    https://github.com/SQ9MDD/RS41-APRS-tracker
    https://github.com/mikaelnousiainen/RS41ng
    (Unknown firmware with tocall APBCRS)

    """

    for sat_filter in ['S0', 'Sats=0', 'Sat=0']:
        if sat_filter in payload['comment']:
            return {'sats': 0}
    
    return {}



if __name__ == "__main__":
    # Some test payload data.

    data = [
        # Nothing extractable from this.
        {'software_name': 'aprs', 'aprs_tocall': 'TW1VU7-2', 'uploader_callsign': 'HB9BB', 'path': 'WIDE1-1,WIDE2-1,qAR,HB9BB', 'time_received': '2023-04-14T05:01:42.107491Z', 'payload_callsign': 'OE9IMJ-11', 'datetime': '2023-04-14T05:01:42.107172Z', 'lat': 47.27616666666667, 'lon': 9.648833333333334, 'alt': 515, 'comment': 'mou CT3001 S8 2.8C  955hPa 3.4V', 'raw': 'OE9IMJ-11>TW1VU7-2,WIDE1-1,WIDE2-1,qAR,HB9BB:`\x7fByl\x1fQO/"9S}mou CT3001 S8 2.8C  955hPa 3.4V', 'modulation': 'APRS'},
        # WB8ELK Skytracker
        {"software_name":"aprs","aprs_tocall":"APELK0","uploader_callsign":"KG6PJG-10","path":"WIDE2-1,qAR,KG6PJG-10","time_received":"2023-04-11T20:21:23.362218Z","payload_callsign":"KJ6IJM-12","datetime":"2023-04-11T20:21:10.000000Z","lat":34.330333333333336,"lon":-116.42416666666666,"alt":1990.9536,"comment":"12 4.34 33 1991 101","raw":"KJ6IJM-12>APELK0,WIDE2-1,qAR,KG6PJG-10:/202110h3419.82N/11625.45WO002/009/A=006532 12 4.34 33 1991 101 |\"+%g$B!-!\"!\"|","modulation":"APRS","position":"34.330333333333336,-116.42416666666666"},
        # StratoTrack	
        {"software_name":"aprs","aprs_tocall":"CQ","uploader_callsign":"SIMLA","path":"WIDE2-1,qAR,SIMLA","time_received":"2023-04-13T15:54:54.121790Z","payload_callsign":"KF0GOR-12","datetime":"2023-04-13T15:54:54.121763Z","lat":40.05766666666667,"lon":-104.36033333333333,"alt":25997.0016,"comment":",StrTrk,84,9,1.46V,-14C,2127Pa,","raw":"KF0GOR-12>CQ,WIDE2-1,qAR,SIMLA:!4003.46N/10421.62WO307/017/A=085292,StrTrk,84,9,1.46V,-14C,2127Pa,","modulation":"APRS","position":"40.05766666666667,-104.36033333333333"},
        # SQ9MDD firmware with no GNSS lock
        {"software_name":"aprs","aprs_tocall":"APZQAP","uploader_callsign":"IR9BV","path":"WIDE1-1,WIDE2-1,qAR,IR9BV","time_received":"2023-04-11T08:48:05.782402Z","payload_callsign":"IT9EWK","datetime":"2023-04-11T08:48:05.782377Z","lat":8.744166666666667,"lon":10.623833333333334,"alt":470.6112,"comment":"P8/S0/T24/V269/ 08:48:05/EV/BT-257.0°C/https://www.pirssicilia.it Beacon CW 432.450 MHz","raw":"IT9EWK>APZQAP,WIDE1-1,WIDE2-1,qAR,IR9BV:!0844.65N/01037.43EO/A=001544/P8/S0/T24/V269/ 08:48:05/EV/BT-257.0°C/https://www.pirssicilia.it Beacon CW 432.450 MHz","modulation":"APRS","position":"8.744166666666667,10.623833333333334"},
        # LightAPRS
        {"software_name":"SondeHub APRS-IS Gateway","software_version":"2023.04.14","uploader_callsign":"N3LLO-1","path":"W1YK-1*,WIDE2-2,qAR,N3LLO-1","time_received":"2023-04-14T19:42:45.578796Z","payload_callsign":"N0LQ-11","datetime":"2023-04-14T19:42:39.000000Z","lat":42.27433333333333,"lon":-71.8075,"alt":145.9992,"comment":"011TxC  36.10C 1034.61hPa  4.93V 08S WPI SDC Gompei-0 Mission","raw":"N0LQ-11>APLIGA,W1YK-1*,WIDE2-2,qAR,N3LLO-1:/194239h4216.46N/07148.45WO353/000/A=000479 011TxC  36.10C 1034.61hPa  4.93V 08S WPI SDC Gompei-0 Mission","aprs_tocall":"APLIGA","modulation":"APRS","position":"42.27433333333333,-71.8075"},
        # Another LightAPRS
        {"software_name":"SondeHub APRS-IS Gateway","software_version":"2023.04.14","uploader_callsign":"KB9LNS-5","path":"WIDE1-1,WIDE2-1,qAO,KB9LNS-5","time_received":"2023-04-14T18:20:04.848026Z","payload_callsign":"KB9LNS-11","datetime":"2023-04-14T18:20:02.000000Z","lat":40.47531868131868,"lon":-88.94545054945056,"alt":261.8232,"comment":"009TxC  23.50C  983.29hPa  4.92V 04S Testing LightAPRS-W 2.0","raw":"KB9LNS-11>APLIGA,WIDE1-1,WIDE2-1,qAO,KB9LNS-5:/182002h4028.51N/08856.72WO158/002/A=000859 009TxC  23.50C  983.29hPa  4.92V 04S Testing LightAPRS-W 2.0 !wta!","aprs_tocall":"APLIGA","modulation":"APRS","position":"40.47531868131868,-88.94545054945056"},
        # RS41ng
        {"software_name":"SondeHub APRS-IS Gateway","software_version":"2023.04.14","uploader_callsign":"F6ASP","path":"WIDE1-1,WIDE2-1,qAO,F6ASP","time_received":"2023-04-14T16:28:43.047244Z","payload_callsign":"F1DZP-11","datetime":"2023-04-14T16:28:43.047218Z","lat":50.94133333333333,"lon":1.8599999999999999,"alt":0.9144000000000001,"comment":"P6S7T29V2947C00 JO00WW - RS41ng radiosonde Toto test","raw":"F1DZP-11>APZ41N,WIDE1-1,WIDE2-1,qAO,F6ASP:!5056.48N/00151.60EO021/000/A=000003/P6S7T29V2947C00 JO00WW - RS41ng radiosonde Toto test","aprs_tocall":"APZ41N","modulation":"APRS","position":"50.94133333333333,1.8599999999999999"},
        # Unknown tracker, sending Sats=0
        {"software_name":"SondeHub APRS-IS Gateway","software_version":"2023.06.24","uploader_callsign":"IS0HHA-12","path":"WIDE2-2,qAR,IS0HHA-12","time_received":"2023-07-29T22:32:17.713152Z","payload_callsign":"IS0HHA-2","datetime":"2023-07-29T22:32:15.000000Z","lat":-21.038369963369963,"lon":115.07478021978022,"alt":0,"comment":"Clb=0.00 Volt=2.76 Sats=0 Fixed=0 - RS41 tracker","raw":"IS0HHA-2>APZQVA,WIDE2-2,qAR,IS0HHA-12:@223215h2102.30S/11504.48EO045/000/A=000000!w5_!Clb=0.00 Volt=2.76 Sats=0 Fixed=0 - RS41 tracker","aprs_tocall":"APZQVA","modulation":"APRS","position":"-21.038369963369963,115.07478021978022"},
        # Unknown tracker, sending Sat=0
        {"software_name":"SondeHub APRS-IS Gateway","software_version":"2023.06.24","uploader_callsign":"IT9DBI-4","path":"IT9LSG-2*,WIDE2-2,qAO,IT9DBI-4","time_received":"2023-07-29T16:16:06.869305Z","payload_callsign":"IT9EJE-12","datetime":"2023-07-29T16:16:06.869281Z","lat":22.591666666666665,"lon":-11.227833333333333,"alt":3099.2064,"comment":"Pkt=2/Sat=0/T25/Mvolts=272/Temp=32.1°C /RS41 Test qrv R3 IR9UBR whatsapp 3393985905","raw":"IT9EJE-12>APZQAP,IT9LSG-2*,WIDE2-2,qAO,IT9DBI-4:!2235.50N/01113.67WO/A=010168/Pkt=2/Sat=0/T25/Mvolts=272/Temp=32.1°C /RS41 Test qrv R3 IR9UBR whatsapp 3393985905","aprs_tocall":"APZQAP","modulation":"APRS","position":"22.591666666666665,-11.227833333333333"}
    ]


    for payload in data:
        print(f"Callsign: {payload['payload_callsign']}, ToCall: {payload['aprs_tocall']}, Comment: {payload['comment']}")
        print(f"Extracted Telemetry: {extract_comment_telemetry(payload)}")

