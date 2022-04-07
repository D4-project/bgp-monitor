import sys, pybgpstream, maxminddb, json

class BGPFilter:
    def __init__(self, country_file, json_output_file):
        """Filter BGP updates

        Args:
            country_file (String): Path to current Geo Open MaxMindDB File 
            json_output_file (File): Where to output json
            record (Boolean): Switching to record mode (retrieve records instead of live stream)
            from_time (TimeStamp): _description_
            until_time (TimeStamp): _description_
        """
        self.country_file = country_file
        self.isStarted = False
        self.collectors=[]
        #self.setRecord(isRecord, start_time, end_time)

    def setJSONOut(self, json_output_file):
        if hasattr(json_output_file, 'write'):
            self.json_out = json_output_file
        else:
            self.json_out = sys.stdout
            raise Exception(f'Unable to use {json_output_file}.')
        

    def setRecord(self, isRecord, start, begin):
        self.isRecord = isRecord
        if self.isRecord:
            if not (self.start_time != self.end_time != ''):
                raise Exception('--until_time and --from_time parameters are required when using record mode', 'red')
            else:
                self.start_time = start
                self.end_time = begin

    def __setCollectors(self):
        pass

    def __pprint(e, f, f_json):
        f_json.write(
            json.dumps(
                {
                    "time": e.time,
                    "type": e.type,
                    "peer": e.peer_address,
                    "peer_number": e.peer_asn,
                    "prefix": e._maybe_field("prefix"),
                    "country": f.get(e._maybe_field("prefix").split("/", 1)[0]),
                }
            )
        )
        # print(e.fields)

    def start(self):
        self.f_country = maxminddb.open_database(self.country_file)
        print(f'Loaded MMDB country by ip file : {self.country_file}')

        """
        try:
            self.f_json = open(self.json_out, 'w')
        except:
            self.f_json = sys.stdout
        """

        if self.isRecord:
            print('Loading records ...')
            self.stream = pybgpstream.BGPStream(collectors=["route-views.sg", "route-views.eqix"], record_type="updates", from_time=self.start_time, until_time=self.end_time)
        else:
            print('Loading live stream ...')
            self.stream = pybgpstream.BGPStream(project="ris-live", collectors=self.collectors, record_type="updates")

        for elem in self.stream:
            self.pprint(elem)


    def stop(self):
        pass

