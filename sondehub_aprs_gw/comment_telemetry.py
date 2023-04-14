#
#   SondeHub APRS Gateway - Comment-Field Telemetry Extractor
#
#   Mark Jessop <vk5qi@rfhead.net>
#
import logging

APRS_S0_TRACKERS = ['APZQAP', 'APZ41N']

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
        if payload['aprs_tocall'].startswith('APELK'):
            return extract_wb8elk_skytracker_telemetry(payload)

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
            output['pressure'] = float(_fields[6][:-2])/100.0

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

        # Space-delimited fields
        _fields = payload['comment'].split(' ')

        # Only extract data if we have the exact number of expected fields.
        if len(_fields) == 5:
            output['sats'] = int(_fields[0])
            output['batt'] = float(_fields[1])
            # The rest of the fields i'm unsure about...

        return output
    except Exception as e:
        logging.exception("Error extracting telemetry from WB8ELK SkyTracker")

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

    To handle this, we add telemetry indicating the lack of GNSS lock, which
    can be filtered on the tracker.

    Examples of firmware that do this:
    https://github.com/SQ9MDD/RS41-APRS-tracker
    https://github.com/mikaelnousiainen/RS41ng

    """

    if "S0" in payload['comment']:
        return {'sats': 0}
    else:
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
        {"software_name":"aprs","aprs_tocall":"APZQAP","uploader_callsign":"IR9BV","path":"WIDE1-1,WIDE2-1,qAR,IR9BV","time_received":"2023-04-11T08:48:05.782402Z","payload_callsign":"IT9EWK","datetime":"2023-04-11T08:48:05.782377Z","lat":8.744166666666667,"lon":10.623833333333334,"alt":470.6112,"comment":"P8/S0/T24/V269/ 08:48:05/EV/BT-257.0°C/https://www.pirssicilia.it Beacon CW 432.450 MHz","raw":"IT9EWK>APZQAP,WIDE1-1,WIDE2-1,qAR,IR9BV:!0844.65N/01037.43EO/A=001544/P8/S0/T24/V269/ 08:48:05/EV/BT-257.0°C/https://www.pirssicilia.it Beacon CW 432.450 MHz","modulation":"APRS","position":"8.744166666666667,10.623833333333334"}
    ]


    for payload in data:
        print(f"Callsign: {payload['payload_callsign']}, ToCall: {payload['aprs_tocall']}, Comment: {payload['comment']}")
        print(f"Extracted Telemetry: {extract_comment_telemetry(payload)}")

