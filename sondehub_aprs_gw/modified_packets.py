#
#   SondeHub APRS Gateway - Modified APRS Packet Detection
#
#   Mark Jessop <vk5qi@rfhead.net>
#
import logging


def is_modified_packet(payload):
    """ 
    Determine if a packet has been modified by an iGate.
    The primary example of this is LoRa iGates that add RSSI/SNR metadata onto the end of comments.
    """

    try:
        # No comment, can't do much
        if payload['comment'] is None:
            return False
        
        # LoRa APRS iGate detection
        # Detect the presence of RSSI, SNR and dB within the comment.
        _comment_upper = payload['comment'].upper()
        if ('RSSI' in _comment_upper) and ('SNR' in _comment_upper) and ('DB' in _comment_upper):
            return True
        
        if ('RSSI=' in _comment_upper) and ('SNR=' in _comment_upper):
            return True
        
        # Check for comments with a "DS -15.75 RS -106" construct on the end
        try:
            _fields = payload['comment'].rstrip().split(" ")
            if (_fields[-2] == "RS") and (_fields[-4] == "DS"):
                _rssi = float(_fields[-1])
                _snr = float(_fields[-3])
                return True
        except:
            pass


    except Exception as e:
        logging.exception("Failed modified packet detection.")

    return False



if __name__ == "__main__":
    # Some test payload data.

    from .test_packets import data


    for payload in data:
        print(f"Callsign: {payload[0]['payload_callsign']}, ToCall: {payload[0]['aprs_tocall']}, Comment: {payload[0]['comment']}")
        print(f"Is a Modified Packet: {is_modified_packet(payload[0])}")

