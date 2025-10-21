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
APRS_S0_TRACKERS = ['APBCRS', 'APZQVA']

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

        # LightAPRS / LightAPRS LoRa
        if payload['aprs_tocall'] == 'APLIGA' or payload['aprs_tocall'] == 'APLIGP':
            return extract_lightaprs_telemetry(payload)

        # RS41ng / RS41-NFW
        if payload['aprs_tocall'] == 'APZ41N' or payload['aprs_tocall'] == 'APZNFW':
            return extract_RS41ng_telemetry(payload)
        
        # RS41HUP (and variants)
        if payload['aprs_tocall'] == 'APZQAP':
            return extract_RS41HUP_telemetry(payload)

        if payload['aprs_tocall'] == 'APZM20':
            return extract_M20_telemetry(payload)

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

        if payload['aprs_tocall'] == "APLIGP":
            output['model'] = 'LightTracker (LoRa)'

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
        pattern = r'([A-Z])(-?\d+)'
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

def extract_RS41HUP_telemetry(payload):
    """
    Attempt to extract telemetry from a RS41HUP tracker comment field.
    Example: P809S8T-30V127 RS41 Balloon
    Link: https://github.com/whallmann/RS41HUP_V2
    """

    try:
        output = {'model': 'RS41HUP'}

        # Split comment field, telemetry should be the first
        _fields = payload['comment'].split()

        # Extract telemetry segments
        pattern = r'([A-Z])(-?\d+)'
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
                output['batt'] = int(_data)/100.0

        return output

    except Exception as e:
        logging.exception("Error extracting telemetry from RS41HUP telemetry")

    return {}

def extract_M20_telemetry(payload):
    """
    Attempt to extract telemetry from a M20 tracker comment field.
    Example: C5S6R0T23P10002E-349V2176 M20 radiosonde test
    Link: https://github.com/sq2ips/m20-custom-firmware
    """

    try:
        output = {'model': 'M20'}

        # Split comment field, telemetry should be the first
        _fields = payload['comment'].split()

        # Extract telemetry segments
        pattern = r'([A-Z])(-?\d+)'
        _matches = re.findall(pattern, _fields[0])

        # Iterate through the found matches, and look for specific identifiers
        for _telem in _matches:
            _type = _telem[0]
            _data = _telem[1]

            if _type == 'C':
                output['frame'] = int(_data)
            elif _type == 'S':
                output['sats'] = int(_data)
            elif _type == 'R':
                output['gps_restarts'] = int(_data)
            elif _type == 'T':
                output['temp'] = int(_data)
            elif _type == 'E':
                output['ext_temp'] = int(_data)/10.0
            elif _type == 'P':
                output['ext_pressure'] = int(_data)/10.0
            elif _type == 'V':
                output['batt'] = int(_data)/1000.0

        return output

    except Exception as e:
        logging.exception("Error extracting telemetry from M20 telemetry")

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

    from .test_packets import not_modified


    for payload in not_modified:
        print(f"Callsign: {payload['payload_callsign']}, ToCall: {payload['aprs_tocall']}, Comment: {payload['comment']}")
        print(f"Extracted Telemetry: {extract_comment_telemetry(payload)}")

