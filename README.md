WIP

Sondehub APRS Gateway
==

This gateway scans for APRS positions (not objects) that are using the balloon symbol and uploads them to the SondeHub database.

Filters
--
Currently the following filters apply. Other requirements may be added in the future.

The position must
 - Contain the balloon symbol
 - Not contain `NSM is Not Sonde Monitor` in the comment field
 - Not contain `SONDEGATE`
 - Not sent to `APHAX` (SM2APRS by PY2UEP)