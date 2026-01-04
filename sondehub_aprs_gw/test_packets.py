import unittest

from . import modified_packets, comment_telemetry


modified = [
        # These packets have been modified by an iGate
        ({"software_name":"SondeHub APRS-IS Gateway","software_version":"abc2655","uploader_callsign":"OK1MX-12","path":"OK2ZAW-17*,qAS,OK1MX-12","time_received":"2024-08-14T13:41:00.932669Z","payload_callsign":"SP0LND-3","datetime":"2024-08-14T13:41:00.932648Z","lat":52.397666666666666,"lon":21.093666666666667,"alt":12841.5288,"comment":"P675S25F0R0N31Q1 S  DP_RSSI: -118 dBm DP_SNR: -17.25 dB","raw":"SP0LND-3>APLRG1,OK2ZAW-17*,qAS,OK1MX-12:!5223.86N/02105.62EO122/056/A=042131/P675S25F0R0N31Q1 S  DP_RSSI: -118 dBm DP_SNR: -17.25 dB ","aprs_tocall":"APLRG1","modulation":"APRS","position":"52.397666666666666,21.093666666666667"},{}),
        ({"software_name":"SondeHub APRS-IS Gateway","software_version":"abc2655","uploader_callsign":"SQ6SLB-10","path":"qAS,SQ6SLB-10","time_received":"2024-08-14T12:53:36.845271Z","payload_callsign":"SP0LND-3","datetime":"2024-08-14T12:53:36.845245Z","lat":52.7645,"lon":20.028833333333335,"alt":12911.937600000001,"comment":"P567S30F0R0N31Q1 S rssi: -117.25dBm, snr: -3.25dB, err: -5131Hz","raw":"SP0LND-3>APLRG1,qAS,SQ6SLB-10:!5245.87N/02001.73EO117/054/A=042362/P567S30F0R0N31Q1 S rssi: -117.25dBm, snr: -3.25dB, err: -5131Hz","aprs_tocall":"APLRG1","modulation":"APRS","position":"52.7645,20.028833333333335"},{}),
        ({"software_name":"SondeHub APRS-IS Gateway","software_version":"abc2655","uploader_callsign":"SQ6SLB-10","path":"qAS,SQ6SLB-10","time_received":"2024-08-14T12:47:02.523385Z","payload_callsign":"SP0LND-3","datetime":"2024-08-14T12:47:02.523362Z","lat":52.807833333333335,"lon":19.885666666666665,"alt":12903.708,"comment":"P552S30F0R0N31Q1 S rssi: -109.00dBm, snr: 1.00dB, err: -5111Hz","raw":"SP0LND-3>APLRG1,qAS,SQ6SLB-10:!5248.47N/01953.14EO115/052/A=042335/P552S30F0R0N31Q1 S rssi: -109.00dBm, snr: 1.00dB, err: -5111Hz","aprs_tocall":"APLRG1","modulation":"APRS","position":"52.807833333333335,19.885666666666665"},{}),
        ({"software_name":"SondeHub APRS-IS Gateway","software_version":"abc2655","uploader_callsign":"OK2ZAW-1","path":"qAS,OK2ZAW-1","time_received":"2024-08-14T12:47:02.262823Z","payload_callsign":"SP0LND-3","datetime":"2024-08-14T12:47:02.262801Z","lat":52.807833333333335,"lon":19.885666666666665,"alt":12903.708,"comment":"P552S30F0R0N31Q1 S  SNR=-18dB RSSI=-82db","raw":"SP0LND-3>APLRG1,qAS,OK2ZAW-1:!5248.47N/01953.14EO115/052/A=042335/P552S30F0R0N31Q1 S  SNR=-18dB RSSI=-82db","aprs_tocall":"APLRG1","modulation":"APRS","position":"52.807833333333335,19.885666666666665"},{}),
        ({"software_name":"SondeHub APRS-IS Gateway","software_version":"abc2655","uploader_callsign":"OK2ZAW-1","path":"qAS,OK2ZAW-1","time_received":"2024-08-14T12:47:02.262823Z","payload_callsign":"SP0LND-3","datetime":"2024-08-14T12:47:02.262801Z","lat":52.807833333333335,"lon":19.885666666666665,"alt":12903.708,"comment":"P3S15O16F1N2 FT0 DS -15.75 RS -106","raw":"SP0LND-2>APLAIR,NOHUB,qAS,OK5TVR-15:!5032.81N/01531.81EO208/054/A=042250/P3S15O16F1N2 FT0 DS -15.75 RS -106","aprs_tocall":"APLRG1","modulation":"APRS","position":"52.807833333333335,19.885666666666665"},{}),
        ({"software_name":"SondeHub APRS-IS Gateway","software_version":"abc2655","uploader_callsign":"OK2ZAW-1","path":"qAS,OK2ZAW-1","time_received":"2024-08-14T12:47:02.262823Z","payload_callsign":"SP0LND-3","datetime":"2024-08-14T12:47:02.262801Z","lat":52.807833333333335,"lon":19.885666666666665,"alt":12903.708,"comment":"P12S15O19F1N2 FT0 SNR=-16.50 RSSI=-122","raw":"SP0LND-2>APLAIR,NOHUB,qAR,OK1KRE-1:!5017.38N/01518.84EO207/057/A=042125/P12S15O19F1N2 FT0 SNR=-16.50 RSSI=-122","aprs_tocall":"APLRG1","modulation":"APRS","position":"52.807833333333335,19.885666666666665"},{}),

]
not_modified = [
        # These packets have not:
        ({"software_name":"SondeHub APRS-IS Gateway","software_version":"abc2655","uploader_callsign":"SP3QYJ-7","path":"qAR,SP3QYJ-7","time_received":"2024-08-14T13:39:37.023694Z","payload_callsign":"SP0LND-3","datetime":"2024-08-14T13:39:37.023671Z","lat":52.40866666666667,"lon":21.065,"alt":12826.5936,"comment":"P672S25F0R0N31Q1 S","raw":"SP0LND-3>APLRG1,qAR,SP3QYJ-7:!5224.52N/02103.90EO122/056/A=042082/P672S25F0R0N31Q1 S ","aprs_tocall":"APLRG1","modulation":"APRS","position":"52.40866666666667,21.065"},
         {}),
        # Nothing extractable from this.
        ({'software_name': 'aprs', 'aprs_tocall': 'TW1VU7-2', 'uploader_callsign': 'HB9BB', 'path': 'WIDE1-1,WIDE2-1,qAR,HB9BB', 'time_received': '2023-04-14T05:01:42.107491Z', 'payload_callsign': 'OE9IMJ-11', 'datetime': '2023-04-14T05:01:42.107172Z', 'lat': 47.27616666666667, 'lon': 9.648833333333334, 'alt': 515, 'comment': 'mou CT3001 S8 2.8C  955hPa 3.4V', 'raw': 'OE9IMJ-11>TW1VU7-2,WIDE1-1,WIDE2-1,qAR,HB9BB:`\x7fByl\x1fQO/"9S}mou CT3001 S8 2.8C  955hPa 3.4V', 'modulation': 'APRS'},
         {}),
        # WB8ELK Skytracker
        ({"software_name":"aprs","aprs_tocall":"APELK0","uploader_callsign":"KG6PJG-10","path":"WIDE2-1,qAR,KG6PJG-10","time_received":"2023-04-11T20:21:23.362218Z","payload_callsign":"KJ6IJM-12","datetime":"2023-04-11T20:21:10.000000Z","lat":34.330333333333336,"lon":-116.42416666666666,"alt":1990.9536,"comment":"12 4.34 33 1991 101","raw":"KJ6IJM-12>APELK0,WIDE2-1,qAR,KG6PJG-10:/202110h3419.82N/11625.45WO002/009/A=006532 12 4.34 33 1991 101 |\"+%g$B!-!\"!\"|","modulation":"APRS","position":"34.330333333333336,-116.42416666666666"},
         {'model': 'WB8ELK SkyTracker', 'sats': 12, 'solar_panel': 4.34, 'temp': 33.0, 'frame': 101}),
        # StratoTrack	
        ({"software_name":"aprs","aprs_tocall":"CQ","uploader_callsign":"SIMLA","path":"WIDE2-1,qAR,SIMLA","time_received":"2023-04-13T15:54:54.121790Z","payload_callsign":"KF0GOR-12","datetime":"2023-04-13T15:54:54.121763Z","lat":40.05766666666667,"lon":-104.36033333333333,"alt":25997.0016,"comment":",StrTrk,84,9,1.46V,-14C,2127Pa,","raw":"KF0GOR-12>CQ,WIDE2-1,qAR,SIMLA:!4003.46N/10421.62WO307/017/A=085292,StrTrk,84,9,1.46V,-14C,2127Pa,","modulation":"APRS","position":"40.05766666666667,-104.36033333333333"},
         {'model': 'StratoTrack', 'frame': 84, 'sats': 9, 'batt': 1.46, 'temp': -14.0, 'ext_pressure': 21.27}),
        # SQ9MDD firmware with no GNSS lock
        ({"software_name":"aprs","aprs_tocall":"APZQAP","uploader_callsign":"IR9BV","path":"WIDE1-1,WIDE2-1,qAR,IR9BV","time_received":"2023-04-11T08:48:05.782402Z","payload_callsign":"IT9EWK","datetime":"2023-04-11T08:48:05.782377Z","lat":8.744166666666667,"lon":10.623833333333334,"alt":470.6112,"comment":"P8/S0/T24/V269/ 08:48:05/EV/BT-257.0°C/https://www.pirssicilia.it Beacon CW 432.450 MHz","raw":"IT9EWK>APZQAP,WIDE1-1,WIDE2-1,qAR,IR9BV:!0844.65N/01037.43EO/A=001544/P8/S0/T24/V269/ 08:48:05/EV/BT-257.0°C/https://www.pirssicilia.it Beacon CW 432.450 MHz","modulation":"APRS","position":"8.744166666666667,10.623833333333334"},
         {'model': 'RS41HUP', 'frame': 8, 'sats': 0, 'temp': 24, 'batt': 2.69}),
        # LightAPRS
        ({"software_name":"SondeHub APRS-IS Gateway","software_version":"2023.04.14","uploader_callsign":"N3LLO-1","path":"W1YK-1*,WIDE2-2,qAR,N3LLO-1","time_received":"2023-04-14T19:42:45.578796Z","payload_callsign":"N0LQ-11","datetime":"2023-04-14T19:42:39.000000Z","lat":42.27433333333333,"lon":-71.8075,"alt":145.9992,"comment":"011TxC  36.10C 1034.61hPa  4.93V 08S WPI SDC Gompei-0 Mission","raw":"N0LQ-11>APLIGA,W1YK-1*,WIDE2-2,qAR,N3LLO-1:/194239h4216.46N/07148.45WO353/000/A=000479 011TxC  36.10C 1034.61hPa  4.93V 08S WPI SDC Gompei-0 Mission","aprs_tocall":"APLIGA","modulation":"APRS","position":"42.27433333333333,-71.8075"},
         {'model': 'LightAPRS', 'frame': 11, 'temp': 36.1, 'ext_pressure': 1034.61, 'batt': 4.93, 'sats': 8}),
        # Another LightAPRS
        ({"software_name":"SondeHub APRS-IS Gateway","software_version":"2023.04.14","uploader_callsign":"KB9LNS-5","path":"WIDE1-1,WIDE2-1,qAO,KB9LNS-5","time_received":"2023-04-14T18:20:04.848026Z","payload_callsign":"KB9LNS-11","datetime":"2023-04-14T18:20:02.000000Z","lat":40.47531868131868,"lon":-88.94545054945056,"alt":261.8232,"comment":"009TxC  23.50C  983.29hPa  4.92V 04S Testing LightAPRS-W 2.0","raw":"KB9LNS-11>APLIGA,WIDE1-1,WIDE2-1,qAO,KB9LNS-5:/182002h4028.51N/08856.72WO158/002/A=000859 009TxC  23.50C  983.29hPa  4.92V 04S Testing LightAPRS-W 2.0 !wta!","aprs_tocall":"APLIGA","modulation":"APRS","position":"40.47531868131868,-88.94545054945056"},
         {'model': 'LightAPRS', 'frame': 9, 'temp': 23.5, 'ext_pressure': 983.29, 'batt': 4.92, 'sats': 4}),
        # RS41ng
        ({"software_name":"SondeHub APRS-IS Gateway","software_version":"2023.04.14","uploader_callsign":"F6ASP","path":"WIDE1-1,WIDE2-1,qAO,F6ASP","time_received":"2023-04-14T16:28:43.047244Z","payload_callsign":"F1DZP-11","datetime":"2023-04-14T16:28:43.047218Z","lat":50.94133333333333,"lon":1.8599999999999999,"alt":0.9144000000000001,"comment":"P6S7T29V2947C00 JO00WW - RS41ng radiosonde Toto test","raw":"F1DZP-11>APZ41N,WIDE1-1,WIDE2-1,qAO,F6ASP:!5056.48N/00151.60EO021/000/A=000003/P6S7T29V2947C00 JO00WW - RS41ng radiosonde Toto test","aprs_tocall":"APZ41N","modulation":"APRS","position":"50.94133333333333,1.8599999999999999"},
         {'model': 'RS41ng', 'frame': 6, 'sats': 7, 'temp': 29, 'batt': 2.947}),
        # RS41HUP
        ({"software_name":"SondeHub APRS-IS Gateway","software_version":"ce4b139","uploader_callsign":"DB0FRI","path":"WIDE1-1,qAO,DB0FRI","time_received":"2024-06-24T03:48:16.565918Z","payload_callsign":"PD3EGE-7","datetime":"2024-06-24T03:48:16.565896Z","lat":50.77733333333333,"lon":4.652333333333333,"alt":13610.234400000001,"comment":"P809S8T-30V127 RS41 Balloon","raw":"PD3EGE-7>APZQAP,WIDE1-1,qAO,DB0FRI:!5046.64N/00439.14EO/A=044653/P809S8T-30V127 RS41 Balloon","aprs_tocall":"APZQAP","modulation":"APRS","position":"50.77733333333333,4.652333333333333"},
         {'model': 'RS41HUP', 'frame': 809, 'sats': 8, 'temp': -30, 'batt': 1.27}),
        # Another RS41ng packet, with a negative temperature
        ({"software_name":"SondeHub APRS-IS Gateway","software_version":"71e6068","uploader_callsign":"DB0FRI-10","path":"WIDE1-1,WIDE2-1,qAU,DB0FRI-10","time_received":"2023-09-29T08:51:27.586394Z","payload_callsign":"DJ9AS-11","datetime":"2023-09-29T08:51:27.586372Z","lat":51.150333333333336,"lon":7.582333333333334,"alt":26406.0432,"comment":"P436S10T-8V2786C09","raw":"DJ9AS-11>APZ41N,WIDE1-1,WIDE2-1,qAU,DB0FRI-10:!5109.02N/00734.94EO305/003/A=086634/P436S10T-8V2786C09","aprs_tocall":"APZ41N","modulation":"APRS","model":"RS41ng","frame":436,"sats":10,"batt":2.786,"position":"51.150333333333336,7.582333333333334"},
         {'model': 'RS41ng', 'frame': 436, 'sats': 10, 'temp': -8, 'batt': 2.786}),
        # Unknown tracker, sending Sats=0
        ({"software_name":"SondeHub APRS-IS Gateway","software_version":"2023.06.24","uploader_callsign":"IS0HHA-12","path":"WIDE2-2,qAR,IS0HHA-12","time_received":"2023-07-29T22:32:17.713152Z","payload_callsign":"IS0HHA-2","datetime":"2023-07-29T22:32:15.000000Z","lat":-21.038369963369963,"lon":115.07478021978022,"alt":0,"comment":"Clb=0.00 Volt=2.76 Sats=0 Fixed=0 - RS41 tracker","raw":"IS0HHA-2>APZQVA,WIDE2-2,qAR,IS0HHA-12:@223215h2102.30S/11504.48EO045/000/A=000000!w5_!Clb=0.00 Volt=2.76 Sats=0 Fixed=0 - RS41 tracker","aprs_tocall":"APZQVA","modulation":"APRS","position":"-21.038369963369963,115.07478021978022"},
         {'sats': 0}),
        # Unknown tracker, sending Sat=0
        ({"software_name":"SondeHub APRS-IS Gateway","software_version":"2023.06.24","uploader_callsign":"IT9DBI-4","path":"IT9LSG-2*,WIDE2-2,qAO,IT9DBI-4","time_received":"2023-07-29T16:16:06.869305Z","payload_callsign":"IT9EJE-12","datetime":"2023-07-29T16:16:06.869281Z","lat":22.591666666666665,"lon":-11.227833333333333,"alt":3099.2064,"comment":"Pkt=2/Sat=0/T25/Mvolts=272/Temp=32.1°C /RS41 Test qrv R3 IR9UBR whatsapp 3393985905","raw":"IT9EJE-12>APZQAP,IT9LSG-2*,WIDE2-2,qAO,IT9DBI-4:!2235.50N/01113.67WO/A=010168/Pkt=2/Sat=0/T25/Mvolts=272/Temp=32.1°C /RS41 Test qrv R3 IR9UBR whatsapp 3393985905","aprs_tocall":"APZQAP","modulation":"APRS","position":"22.591666666666665,-11.227833333333333"},
         {'model': 'RS41HUP', 'temp': 25}),
        # Light-APRS LoRa-APRS Tracker
        ({"software_name":"SondeHub APRS-IS Gateway","software_version":"c722840","uploader_callsign":"K9WS-10","path":"WIDE1-1,qAR,K9WS-10","time_received":"2024-08-07T21:09:56.355682Z","payload_callsign":"kf0mds-2","datetime":"2024-08-07T21:09:49.000000Z","lat":37.73266666666667,"lon":-121.87616666666666,"alt":892.4544000000001,"comment":"203TXC 31C  911.24hPa 4.5V 14S LoRa APRS LightTracker by TA2MUN & TA2WX","raw":"kf0mds-2>APLIGP,WIDE1-1,qAR,K9WS-10:/210949h3743.96N/12152.57WO032/011/A=002928 203TXC 31C  911.24hPa 4.5V 14S LoRa APRS LightTracker by TA2MUN & TA2WX","aprs_tocall":"APLIGP","modulation":"APRS","position":"37.73266666666667,-121.87616666666666"},
         {'model': 'LightTracker (LoRa)', 'temp': 31.0, 'ext_pressure': 911.24, 'batt': 4.5, 'sats': 14}),
        # check to make sure don't false positive for match DS RS
        ({"software_name":"SondeHub APRS-IS Gateway","software_version":"abc2655","uploader_callsign":"OK2ZAW-1","path":"qAS,OK2ZAW-1","time_received":"2024-08-14T12:47:02.262823Z","payload_callsign":"SP0LND-3","datetime":"2024-08-14T12:47:02.262801Z","lat":52.807833333333335,"lon":19.885666666666665,"alt":12903.708,"comment":"P3S15O16F1N2 FT0 DS foo RS -106","raw":"SP0LND-2>APLAIR,NOHUB,qAS,OK5TVR-15:!5032.81N/01531.81EO208/054/A=042250/P3S15O16F1N2 FT0 DS foo RS -106","aprs_tocall":"APLRG1","modulation":"APRS","position":"52.807833333333335,19.885666666666665"},
         {}),
        # M20
        ({"software_name": "SondeHub APRS-IS Gateway", "software_version": "f226ca1", "uploader_callsign": "SQ2IPS-2", "path": "WIDE1-1,WIDE2-1*,qAO,SQ2IPS-2", "time_received": "2025-10-21T20:11:20.722188Z", "payload_callsign": "SQ2IPS-11", "datetime": "2025-10-20T11:17:00.000000Z", "lat": 54.50580690212797, "lon": 18.538844815003444, "alt": 36479.0736, "comment": "C5S6R0T23P10002E-349V2176A1234 M20 radiosonde test", "raw": "SQ2IPS-11>APRM20,WIDE1-1,WIDE2-1*,qAO,SQ2IPS-2:@201117z/2vc`S1DjO!!C/A=119682C5S6R0T23P10002E-349V2176A1234 M20 radiosonde test", "aprs_tocall": "APRM20", "modulation": "APRS", "position": "54.50580690212797,18.538844815003444"},
         {'model': 'M20', 'frame': 5, 'sats': 6, 'gps_restarts': 0, 'temp': 23, 'ext_pressure': 1000.2, 'ext_temp': -34.9, 'batt': 2.176, 'pv_voltage': 1.234}),
        # RS41-NFW
        ({"software_name": "SondeHub APRS-IS Gateway", "software_version": "2026.01.03", "uploader_callsign": "SP5KAB-2", "path": "WIDE2-1,qAR,SP5KAB-2", "time_received": "2026-01-03T19:00:00.000000Z", "payload_callsign": "SP5FRA-11", "datetime": "2026-01-03T19:00:00.000000Z", "lat": 52.12345, "lon": 20.12345, "alt": 130.1496, "comment": "F2S5V3110C-7I11T-1H88P9967J0R4 test NO flight @RS41-NFW", "raw": "SP5FRA-11>APRNFW,WIDE2-1,qAR,SP5KAB-2:!5212.38N/02058.49EO/A=000427/F2S5V3110C-7I11T-1H88P9967J0R4 test NO flight @RS41-NFW", "aprs_tocall": "APRNFW", "modulation": "APRS", "position": "52.12345,20.12345"},
         {'model': 'RS41-NFW', 'frame': 2, 'sats': 5, 'batt': 3.11, 'ascent_rate': -0.07, 'temp': 11, 'ext_temperature': -1, 'ext_humidity': 88, 'ext_pressure': 996.7, 'jam_warning': 0, 'subtype': 'RSM4x4/5 PCB revision'}),
]

data = modified + not_modified

class TestModified(unittest.TestCase):
    def test_modified_packet_processing(self):
        for payload in modified:
            self.assertTrue(modified_packets.is_modified_packet(payload[0]), msg=payload[0])
    def test_not_modified_packet_processing(self):
        for payload in not_modified:
            self.assertFalse(modified_packets.is_modified_packet(payload[0]), msg=payload[0])

class TestComment(unittest.TestCase):
    def test_comment_telemetry(self):
        for payload in not_modified:
            telm = comment_telemetry.extract_comment_telemetry(payload[0])
            self.assertEqual(telm,payload[1])
    def test_comment_none(self):
        telm = comment_telemetry.extract_comment_telemetry(
            {'software_name': 'aprs', 'aprs_tocall': 'TW1VU7-2', 'uploader_callsign': 'HB9BB', 'path': 'WIDE1-1,WIDE2-1,qAR,HB9BB', 'time_received': '2023-04-14T05:01:42.107491Z', 'payload_callsign': 'OE9IMJ-11', 'datetime': '2023-04-14T05:01:42.107172Z', 'lat': 47.27616666666667, 'lon': 9.648833333333334, 'alt': 515, 'comment': 'mou CT3001 S8 2.8C  955hPa 3.4V', 'raw': 'OE9IMJ-11>TW1VU7-2,WIDE1-1,WIDE2-1,qAR,HB9BB:`\x7fByl\x1fQO/"9S}mou CT3001 S8 2.8C  955hPa 3.4V', 'modulation': 'APRS'},
        )
        self.assertEqual(telm,{})
    def test_sats0(self):
        for payload in [
            # Unknown tracker, sending Sats=0
            {"software_name":"SondeHub APRS-IS Gateway","software_version":"2023.06.24","uploader_callsign":"IS0HHA-12","path":"WIDE2-2,qAR,IS0HHA-12","time_received":"2023-07-29T22:32:17.713152Z","payload_callsign":"IS0HHA-2","datetime":"2023-07-29T22:32:15.000000Z","lat":-21.038369963369963,"lon":115.07478021978022,"alt":0,"comment":"Clb=0.00 Volt=2.76 Sats=0 Fixed=0 - RS41 tracker","raw":"IS0HHA-2>APZQVA,WIDE2-2,qAR,IS0HHA-12:@223215h2102.30S/11504.48EO045/000/A=000000!w5_!Clb=0.00 Volt=2.76 Sats=0 Fixed=0 - RS41 tracker","aprs_tocall":"APZQVA","modulation":"APRS","position":"-21.038369963369963,115.07478021978022"},
            # Unknown tracker, sending Sat=0
            {"software_name":"aprs","aprs_tocall":"APZQAP","uploader_callsign":"IR9BV","path":"WIDE1-1,WIDE2-1,qAR,IR9BV","time_received":"2023-04-11T08:48:05.782402Z","payload_callsign":"IT9EWK","datetime":"2023-04-11T08:48:05.782377Z","lat":8.744166666666667,"lon":10.623833333333334,"alt":470.6112,"comment":"P8/S0/T24/V269/ 08:48:05/EV/BT-257.0°C/https://www.pirssicilia.it Beacon CW 432.450 MHz","raw":"IT9EWK>APZQAP,WIDE1-1,WIDE2-1,qAR,IR9BV:!0844.65N/01037.43EO/A=001544/P8/S0/T24/V269/ 08:48:05/EV/BT-257.0°C/https://www.pirssicilia.it Beacon CW 432.450 MHz","modulation":"APRS","position":"8.744166666666667,10.623833333333334"},
        ]:
            telm = comment_telemetry.extract_comment_telemetry(payload)
            self.assertEqual(telm['sats'], 0)
    def test_StrTrk(self):
        telm = comment_telemetry.extract_comment_telemetry(
            {"software_name":"aprs","aprs_tocall":"CQ","uploader_callsign":"SIMLA","path":"WIDE2-1,qAR,SIMLA","time_received":"2023-04-13T15:54:54.121790Z","payload_callsign":"KF0GOR-12","datetime":"2023-04-13T15:54:54.121763Z","lat":40.05766666666667,"lon":-104.36033333333333,"alt":25997.0016,
             "comment":",StrTrk,84,9,1.46V,-14C,2127Pa,","raw":"KF0GOR-12>CQ,WIDE2-1,qAR,SIMLA:!4003.46N/10421.62WO307/017/A=085292,StrTrk,84,9,1.46V,-14C,2127Pa,","modulation":"APRS","position":"40.05766666666667,-104.36033333333333"},
        )
        self.assertEqual(telm['batt'], 1.46)
        self.assertEqual(telm['temp'], -14.0)
        self.assertEqual(telm['ext_pressure'], 2127/100.0)
        self.assertEqual(telm['frame'], 84)
        self.assertEqual(telm['sats'], 9)

if __name__ == '__main__':
    unittest.main()
