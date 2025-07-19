# SondeHub APRS Gateway

This gateway takes a feed of traffic from APRS-IS, looks for APRS position reports that might be a high-altitude balloon, and uploads them to the SondeHub-Amateur database.

It also uploads the station locations of APRS receivers, if their position has recently been uploaded to APRS-IS.

**This software runs within the SondeHub AWS ecosystem, and cannot be run elsewhere as it requires direct access to the SondeHub database. It does not receive APRS packets directly from a radio or act as an APRS iGate, for that you need to run other software such as [direwolf](https://github.com/wb2osz/direwolf).** 

Please contact us if you are having issues with getting your APRS payload on the SondeHub-Amateur map. 

### Contacts
* [Mark Jessop](https://github.com/darksidelemm) - vk5qi@rfhead.net
* [Michaela Wheeler](https://github.com/TheSkorm) - radiosonde@michaela.lgbt

## Packet Filtering
Currently the following filters apply. Other requirements may be added in the future.

The position must:
 - Be a position report (not an object). This can be compressed, uncompressed, or mic-e format.
 - Use the balloon symbol (Primary Symbol Table, 'O')

We block packets containing the following strings in the comment fields:
 - `NSM is Not Sonde Monitor`
 - `SondeID`
 - `Ozonesonde`
 - `Recupero Radiosonde`

We block packets from the following 'tocall' destinations:
 - `APHAX` - SM2APRS Software
 - `APAT51` - Anytone AT-D578UV APRS mobile radios
 - `APRDR` - APRSDroid
 - `APRARX` - Old radiosonde_auto_rx versions
 - `OGFLR` - Packets arriving via an Open Glider Network Gateway
 - `SONDA` - Another kind of radiosonde gateway
 - `APLAIR` - SP0LND LoRa-APRS trackers (on request from author)
 - `APZHUB` - SQ2CPA wspr2sondehub scripts (on request from author, this software uploads to SondeHub-Amateur separately)

We block packets with the following in their path:
 - `SONDEGATE` - Radiosonde Gateways
 - `NOHUB` - Use this if you want to send packets into APRS-IS that you *don't* want imported.

We block packets from the following source callsigns:
 - Any source callsign containing `WIDE`, which usually indicates a corrupted packet.

We block packets where RSSI and SNR metadata has been added onto the end of the comment field. This is usually done by LoRa-APRS iGates, and causes issues with de-duping and speed calculations. If you are flying a payload which actually is reporting some valid RSSI or SNR data within the comment, please contact us!

## Timestamps
The APRS-IS importer will parse and use timestamps included in APRS packets, e.g. the `HHMMSSh` format. Note that we assume that all timestamps are in UTC. If this is not the case, you may experience strange behaviour on the tracker!

## Telemetry
Currently we do not support decoding APRS telemetry packets, though this may be added in the future.

There is some limited support for decoding telemetry from the comment field of the following APRS tracker models:
- High Altitude Science [StratoTrack](https://www.highaltitudescience.com/products/stratotrack-aprs-transmitter)
  - Allowed Format: `,StrTrk,84,9,1.46V,-14C,2127Pa,`
- WB8ELK [SkyTracker](https://gmigliarini.wixsite.com/wb8elk)
  - Allowed Format: `12 4.34 33 1991 101`
- [LightAPRS](https://github.com/lightaprs/LightAPRS-W-1.0) (Also works for LightAPRS LoRa software)
  - Allowed Format: `015TxC 29.00C 1019.86hPa 4.59V 06S Custom comment here`
- [RS41ng](https://github.com/mikaelnousiainen/RS41ng/)
  - Allowed Format: `P6S7T29V2947C00`    (Note - Voltage is in mV)
- [RS41HUP-V2](https://github.com/whallmann/RS41HUP_V2)
  - Allowed Format: `P809S8T-30V127`     (Note - Voltage is in hundredths of a Volt)

Note that the telemetry must be exactly in the provided format, else parsing will fail.

If you would like support added for another tracker model, please contact us.

## Chase-Car Positions
Chase cars can have their positions plotted on the SondeHub-Amateur tracker by adding `SHUB` or `SHUB1-1` to their APRS path. Note that we do not support APRS chase car position uploading for the 'professional' (meteorological) SondeHub tracker.

## Testing & Development

Create and enter a Python venv
```
$ python3 -m venv venv
$ . venv/bin/activate
```

Install dependencies:
```
$ pip install -r requirements.txt
```

Run with:
```
CALLSIGN=YOURCALL python -m sondehub_aprs_gw
```

This will run and output debug info, but will not upload to SondeHub unless the SNS environment variable is set.
