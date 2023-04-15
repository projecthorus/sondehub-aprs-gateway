# SondeHub APRS Gateway

This gateway takes a feed of traffic from APRS-IS, looks for APRS position reports that might be a high-altitude balloon, and uploads them to the SondeHub-Amateur database.

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

We block packets with the following in their path:
 - `SONDEGATE` - Radiosonde Gateways

We also block packets from the following source callsigns:
 - Any source callsign containing `WIDE`, which usually indicates a corrupted packet.

## Telemetry
Currently we do not support decoding APRS telemetry packets, though this may be added in the future.

There is some limited support for decoding telemetry from the comment field of the following APRS tracker models:
- High Altitude Science [StratoTrack](https://www.highaltitudescience.com/products/stratotrack-aprs-transmitter)
  - Allowed Format: `,StrTrk,84,9,1.46V,-14C,2127Pa,`
- WB8ELK [SkyTracker](https://gmigliarini.wixsite.com/wb8elk)
  - Allowed Format: `12 4.34 33 1991 101`
- [LightAPRS](https://github.com/lightaprs/LightAPRS-W-1.0)
  - Allowed Format: `015TxC 29.00C 1019.86hPa 4.59V 06S Custom comment here`

Note that the telemetry must be exactly in the provided format, else parsing will fail.

If you would like support added for another tracker model, please contact us.


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
