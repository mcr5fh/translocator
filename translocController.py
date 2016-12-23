import datetime
import unirest
import logging

class TranslocController():
    local_address = ""

    local_agency_id = -1
    local_route_number = -1
    local_stop_number = -1

    def __init__(self):
        logging.basicConfig(filename='trans.log',level=logging.DEBUG)

    #returns the minutes until the next bus
    def get_next_bus_arrival(self, agency_id, stop_num):
        logging.debug('agency_id: ')
        logging.debug(agency_id)

        logging.debug('stop_num: ')
        logging.debug(stop_num)

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
        #take off the time zone
        next_time_formatted = next_arrival_time[:-6]
        # its +5 hours in the utc format from transloc
        #TODO: make this a class member
        time_zone = 5
        #create a date time object from it
        next_time_dtobj = datetime.datetime.strptime(next_time_formatted, '%Y-%m-%dT%H:%M:%S')
        logging.debug('timenow(): ')
        logging.debug(datetime.datetime.now())

        next_time_dtobj += datetime.timedelta(0,5*60)
        logging.debug('next time - changed: ')
        logging.debug(next_time_dtobj.now())

        #time_delta = next_time_dtobj - datetime.datetime.now()
        time_delta =  datetime.datetime.now() - next_time_dtobj 
        logging.debug('timeDelta: ')
        logging.debug(time_delta)
        delta_mins = time_delta.seconds / 60
        logging.debug('dmin: ')
        logging.debug(delta_mins)
        return delta_mins

    def set_agency_id(self, a_id):
        agency_id = a_id

    def set_route_number(self, r_num):
        route_number = r_num

    def set_stop_number(self, s_num):
        stop_number = s_num


