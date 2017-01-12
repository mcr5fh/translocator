import datetime
import unirest
import logging
import geocoder

class TranslocController():

    def __init__(self):
        logging.basicConfig(filename='trans.log',level=logging.DEBUG)
        self.local_address = ""
        self.agency_long_name = ""

        self.local_agency_id = -1
        self.local_route_number = -1
        self.local_stop_id = -1
        self.local_stop_id = -1

        self.local_nearby_stops = []
        self.local_nearby_stop_ids = []
        self.getting_options = False

    def set_location(self, address):
        #local_address = address
        g = geocoder.google(address)
        #<[OK] Google - Geocode [608 Preston Pl, Charlottesville, VA 22903, USA]>
        # g.bbox
        # {'northeast': [38.0429164802915, -78.49673836970848], 'southwest': [38.0402185197085, -78.49943633029149]}
        
        #just goes in order as you'd expect from the api

        base_url = "https://transloc-api-1-2.p.mashape.com/agencies.json?callback=call&"
        geo_area = "geo_area="+str(g.bbox['northeast'][0])+"%2C+"+ str(g.bbox['northeast'][1]) + "%7C" \
                        + str(g.bbox['southwest'][0])+"%2C+"+ str(g.bbox['southwest'][1]) 

        response = unirest.get(base_url + geo_area,
          headers={
            "X-Mashape-Key": "P5XVDHDhPEmshrYNeT29XndUunS4p1EPDrOjsnosBj9nVdvjit",
            "Accept": "application/json"
          }
        )
        # print(response.body['data'][0]['long_name'])
        # print(response.body['data'][0]['agency_id'])
        self.local_address = address
        self.local_agency_id = response.body['data'][0]['agency_id']
        self.acgency_long_name = response.body['data'][0]['long_name']

    #Will return a list of strings of the stops in the vicinity
    def set_closest_stop(self, address = None):
        if(address != None):
            self.set_location(address)

        if(self.local_agency_id == -1):
            logging.error('Agency id has not been set')
            return None

        g = geocoder.google(self.local_address)
        base_url = "https://transloc-api-1-2.p.mashape.com/stops.json?agencies=347&callback=call&"
        try: 
            geo_area = "geo_area="+str(g.bbox['northeast'][0])+"%2C+" \
                            + str(g.bbox['northeast'][1]) + "%7C" \
                            + str(g.bbox['southwest'][0])+"%2C+"  \
                            + str(g.bbox['southwest'][1]) 
        except Exception as e:
            print(e.response['Error']['Message'])
            print address
            return []

        response = unirest.get(base_url + geo_area,
          headers={
            "X-Mashape-Key": "P5XVDHDhPEmshrYNeT29XndUunS4p1EPDrOjsnosBj9nVdvjit",
            "Accept": "application/json"
          }
        )
        stop_list_str = []
        stop_list_id = []
        for stop_data in response.body['data']:
            stop_list_str.append(stop_data['name'].encode('utf8'))
            stop_list_id.append(stop_data['stop_id'])

        #logging.info(stop_list)
        self.local_nearby_stops = stop_list_str
        self.local_nearby_stop_ids = stop_list_id
        return stop_list_str


    #returns the minutes until the next bus
    def get_next_bus_arrival(self, agency_id, stop_num):
        base_url = "https://transloc-api-1-2.p.mashape.com/arrival-estimates.json?agencies="
        base_url += str(agency_id)
        base_url += "&callback=call&stops="
        base_url += str(stop_num)

        response = unirest.get(base_url,
          headers={
            "X-Mashape-Key": "P5XVDHDhPEmshrYNeT29XndUunS4p1EPDrOjsnosBj9nVdvjit",
            "Accept": "application/json"
          }
        )
        
        #accesses the first (next arriving bus from the list)
        next_arrival_time = response.body['data'][0]['arrivals'][0]['arrival_at']
        #gives us something like this: '2016-12-22T17:31:55-05:00'
        #take off the time zone: '-05:00'
        next_time_formatted = next_arrival_time[:-6]
        # its +5 hours in the utc format from transloc
        time_zone = next_arrival_time[-6:]
        time_zone_offset = int(time_zone[1:3])
        #create a date time object from it
        next_time_dtobj = datetime.datetime.strptime(next_time_formatted, '%Y-%m-%dT%H:%M:%S')
        next_time_dtobj += datetime.timedelta(0,time_zone_offset*60*60)

        time_delta = next_time_dtobj - datetime.datetime.now() 
        delta_mins = time_delta.seconds / 60

        return delta_mins

# ---------- Getters and Setters ---------- 
    def get_getting_options(self):
        return self.getting_options

    def set_getting_options(self, status):
        self.getting_options = status

    def set_stop_id_from_stop_list(self, stop_list_index):
        self.local_stop_id = self.local_nearby_stop_ids[stop_list_index]

    def set_stop_id(self, stop_id):
        self.local_stop_id = stop_id

    def get_stop_id(self):
        return self.local_stop_id

    def set_agency_id(self, a_id):
        self.local_agency_id = a_id

    def get_agency_id(self):
        return self.local_agency_id

    def get_closest_stop_list(self):
        return self.local_nearby_stops




