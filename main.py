
#!/usr/bin/env python
from sys import prefix
import pybgpstream
import maxminddb

ip_country_mmdb_path_p = '2022-03-31-GeoOpen-Country.mmdb'
until_time_p = ""
from_time_p = ""


# Load default AS File
#with maxminddb.open_database(ip_country_mmdb_path_p) as reader:
    #print(reader.get('152.216.7.110'))

    # Live BGP Stream
stream = pybgpstream.BGPStream(project="ris-live",record_type="updates")                               
                                #filter="collector rrc00"
    #                               from_time="2022-01-01 10:00:00",until_time="2022-01-04 11:10:00",


for elem in stream:
    print(elem.fields.get('prefix', ''))
        #Check for each record, if suspect 
        # -> 
