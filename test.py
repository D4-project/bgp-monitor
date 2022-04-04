#!/usr/bin/env python
from sys import prefix

import maxminddb

ip_country_mmdb_path_p = '2022-03-31-GeoOpen-Country.mmdb'

with maxminddb.open_database(ip_country_mmdb_path_p) as reader:
    print(reader.get('185.173.181.29'))
