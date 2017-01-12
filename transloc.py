import urllib2
import json
#import pymysql
#import re
import unirest
#pymysql.install_as_MySQLdb()
#for dynamoDB
from dynamoClient import DynamoClient
#transloc API
from translocController import TranslocController
####################################################################

tableName = "TranslocatorUserInfo"
first_session = True
mySkillId = "amzn1.ask.skill.b9945778-9da9-4879-a534-97309608acae"

####################################################################
transController = TranslocController()
dynamoClient = DynamoClient(tableName)


#"amzn1.ask.skill.7a1c9174-26ed-4dcb-a02d-8be0b35a6947"): - logan's

def lambda_handler(event, context):
    if (event["session"]["application"]["applicationId"] != mySkillId):
        raise ValueError("Invalid Application ID: ", event["session"]["application"]["applicationId"])
    
    if event["session"]["new"]:
        on_session_started({"requestId": event["request"]["requestId"]}, event["session"])

    if event["request"]["type"] == "LaunchRequest":
        return on_launch(event["request"], event["session"])
    elif event["request"]["type"] == "IntentRequest":
        return on_intent(event["request"], event["session"])
    elif event["request"]["type"] == "SessionEndedRequest":
        return on_session_ended(event["request"], event["session"])

def on_session_started(session_started_request, session):
    print "Starting new session."

def on_launch(launch_request, session):
    return get_welcome_response()

def on_intent(intent_request, session):
    intent = intent_request["intent"]
    intent_name = intent_request["intent"]["name"]

    if first_session:
        dynamo_table_key = session["user"]["userId"]
        dynamoClient = DynamoClient(tableName)
        #check and or set first session could just make a function to catch the except.
        #make this get(uid) if error, then we have to setup, otherwise, were fine

    if intent_name == "GetNearestBus":
        return get_nearest_bus(intent)
    elif intent_name == "ConfigureLocation":
        return configure_location(intent)
    elif intent_name == "GetOption":
        return get_option(intent)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")

def on_session_ended(session_ended_request, session):
    print "Ending session."
    # Cleanup goes here...
    

def handle_session_end_request():
    card_title = "Translocator - Thanks"
    speech_output = "Thank you for using the translocator skill.  See you next time!"
    should_end_session = True

    return build_response({}, build_speechlet_response(card_title, speech_output, None, should_end_session))

def get_nearest_bus(intent):
    session_attributes = {}
    card_title = "Transloc nearest bus time"
    speech_output = "You're trying to get a bus time. Awesome."
    reprompt_text = "I'm not sure what you're asking for. "
    should_end_session = False

    #Transloc 
    agency_id = translocController.get_agency_id()
    stop_id = translocController.get_stop_id() 
    
    #Make sure everything is configured
    if(agency_id == -1 or stop_id == -1):
        speech_output = "An error has occured in finding your stop. Please configure location"
        return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

    #sample data
    # min_till_bus = transController.get_next_bus_arrival(347, 4123822)
    min_till_bus = transController.get_next_bus_arrival(agency_id, stop_id)

    speech_output = "The next bus is in " + str(min_till_bus) + " minutes"

    return build_response(session_attributes, build_speechlet_response(
    card_title, speech_output, reprompt_text, should_end_session))

def configure_location(intent):
    session_attributes = {}
    card_title = "Translocator configure location"
    speech_output = "The address you provided does not match the required format. Please try again."
    reprompt_text = "Please provide a valid address. An example is 608 Preston Place, Charlottesville Virginia."
    should_end_session = False

    if "address" in intent["slots"]:
        addr = intent["slots"]["address"]["value"]

        stop_list = transController.set_closest_stop(addr)
        if(len(stop_list) > 1):
            #set list in controller

            #shouldnt need this transController.local_nearby_stops = stop_list
            transController.set_getting_options(True)

            speech_output = "The following stops are available in your area: "
            for index, val in enumerate(stop_list):
                speech_output += "Option " + str(index + 1) + ": " + val + ", "

            speech_output = speech_output[:-2]
            speech_output += ". Select the desired option by saying 'option' followed by the corresponding number."

        else:
            #speech_output = "The address you provided is " + addr
            speech_output = "Your stop is now set to " + stop_list[0]

    return build_response(session_attributes, build_speechlet_response(
    card_title, speech_output, reprompt_text, should_end_session))

def get_option(intent):
    session_attributes = {}
    card_title = "Translocator get option"
    speech_output = "This was not a valid option. Please try again."
    reprompt_text = "Please provide a valid option."
    should_end_session = False

    if transController.get_getting_options() == False:
        speech_output = "Please start by using the keyword configure."

        return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))    

    if "option" in intent["slots"]:
        speech_output = "option is a slot."
        option = intent["slots"]["option"]["value"]
        option = int(option)
        stop_list = transController.get_closest_stop_list()
#       speech_output += " stop_list is " + str(len(stop_list)) + "entries long. provided option: " + option
        if option <= len(stop_list):
            #need the minus ones for indexing
            stop_name = stop_list[option-1]
            speech_output = "You chose option " + str(option) + ": " + stop_name
            #Added this
            transController.set_stop_id(option-1)

            #store the location data
            dynamoClient.store_agency_route_stop(dynamo_table_key, transController.get_agency_id(), 
                                                transController.get_route_id(), stop_name):


    return build_response(session_attributes, build_speechlet_response(
    card_title, speech_output, reprompt_text, should_end_session))    


def get_welcome_response():
    session_attributes = {}
    card_title = "Translocator"
    speech_output = "Welcome to the Translocator skill."
    if first_session:
        speech_output += "Configure your device's location using the " \
        "'configure' keyword, followed by your address."

    reprompt_text = "You can ask when the next bus is coming to your nearest stop." \
                    "You can also configure your device's location by saying configure followed by your address."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        "outputSpeech": {
            "type": "PlainText",
            "text": output
        },
        "card": {
            "type": "Simple",
            "title": title,
            "content": output
        },
        "reprompt": {
            "outputSpeech": {
                "type": "PlainText",
                "text": reprompt_text
            }
        },
        "shouldEndSession": should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        "version": "1.0",
        "sessionAttributes": session_attributes,
        "response": speechlet_response
    }

# def course_when(intent):
#     session_attributes = {}
#     card_title = "LOUIE course times"
#     speech_output = "I'm not sure which course you wanted. " \
#                     "Please try again."
#     reprompt_text = "I'm not sure which course you wanted. " \
#                     "Try asking about Four thousand seven hundred forty for example."
#     should_end_session = False


#     if "coursenum" in intent["slots"]:
#         course_num = intent["slots"]["coursenum"]["value"]

#         course_num_s = course_num.encode('utf8')
#         num = re.sub('[,]', '', course_num_s)
#         #station_code = get_station_code(station_name.lower())

#         conn = pymysql.connect(host='uvaclasses.martyhumphrey.info', port=3306, user='UVAClasses', passwd='WR6V2vxjBbqNqbts', db='uvaclasses')
#         cur = conn.cursor()

#         #check course
#         executeString = '''Select 1 from CS1172Data where number = "%s" ''' % (num)

#         cur.execute(executeString)
#         if cur.fetchall():
#             speech_output = ""
#             executeString = '''Select
#                 DISTINCT Days
#                 from CS1172Data where
#                 NUMBER = "%s"

#                 ''' % (num)

#             cur.execute(executeString)

#             string = "course " + num + " meets at the following times: "
#             count = 0
#             for (meetingTime) in cur:
#                 first = meetingTime[0]
#                 #do some string manipulation
#                 first = re.sub('(Tu)', 'Tuesday ', first)
#                 first = re.sub('(Th)', 'Thursday ', first)
#                 first = re.sub('(Mo)', 'Monday ', first)
#                 first = re.sub('(We)', 'Wednesday ', first)
#                 first = re.sub('(Fr)', 'Friday ', first)
#                 first = re.sub('( - )', ' to ', first)
#                 if(count !=0):
#                     string += ",  {" + first + "}"
#                 else:
#                     string += "{" + first + "}"
#                 count = count + 1


#             speech_output += string
#             reprompt_text = ""

#         cur.close()
#         conn.close()

#     return build_response(session_attributes, build_speechlet_response(
#         card_title, speech_output, reprompt_text, should_end_session))

# def course_where(intent):
#     session_attributes = {}
#     card_title = "LOUIE course locations"
#     speech_output = "I'm not sure which course you wanted. " \
#                     "Please try again."
#     reprompt_text = "I'm not sure which course you wanted. " \
#                     "Try asking about Four thousand seven hundred forty for example."
#     should_end_session = False


#     if "coursenum" in intent["slots"]:
#         course_num = intent["slots"]["coursenum"]["value"]

#         course_num_s = course_num.encode('utf8')
#         num = re.sub('[,]', '', course_num_s)
#         #station_code = get_station_code(station_name.lower())

#         conn = pymysql.connect(host='uvaclasses.martyhumphrey.info', port=3306, user='UVAClasses', passwd='WR6V2vxjBbqNqbts', db='uvaclasses')
#         cur = conn.cursor()

#         #check course
#         executeString = '''Select 1 from CS1172Data where number = "%s" ''' % (num)

#         cur.execute(executeString)
#         if cur.fetchall():
#             speech_output = ""
#             executeString = '''Select
#                 DISTINCT Room
#                 from CS1172Data where
#                 NUMBER = "%s"

#                 ''' % (num)

#             cur.execute(executeString)

#             string = "course " + num + " meets at the following locations: "
#             count = 0
#             for (meetingTime) in cur:
#                 first = meetingTime[0]
                
#                 first = re.sub('(Bldg)', 'Building', first)
#                 first = re.sub('(Engr)', 'Engineering', first)


#                 if(count !=0):
#                     string += ",  {" + first + "}"
#                 else:
#                     string += "{" + first + "}"
#                 count = count + 1


#             speech_output += string
#             reprompt_text = ""

#         cur.close()
#         conn.close()

#     return build_response(session_attributes, build_speechlet_response(
#         card_title, speech_output, reprompt_text, should_end_session))

# def course_seats(intent):
#     session_attributes = {}
#     card_title = "LOUIE course locations"
#     speech_output = "I'm not sure which course you wanted. " \
#                     "Please try again."
#     reprompt_text = "I'm not sure which course you wanted. " \
#                     "Try asking about Four thousand seven hundred forty for example."
#     should_end_session = False


#     if "coursenum" in intent["slots"]:
#         course_num = intent["slots"]["coursenum"]["value"]

#         course_num_s = course_num.encode('utf8')
#         num = re.sub('[,]', '', course_num_s)

#         #station_code = get_station_code(station_name.lower())

#         conn = pymysql.connect(host='uvaclasses.martyhumphrey.info', port=3306, user='UVAClasses', passwd='WR6V2vxjBbqNqbts', db='uvaclasses')
#         cur = conn.cursor()

#         #check course
#         executeString = '''Select 1 from CS1172Data where number = "%s" ''' % (num)

#         cur.execute(executeString)
#         if cur.fetchall():
#             speech_output = ""
            
#             executeString = '''Select
#             SUM(EnrollmentLimit) from CS1172Data where
#             NUMBER = "%s" 
#             ''' % (num)

#             cur.execute(executeString)

#             for val in cur:
#                 offered = val[0]

#             executeString = '''Select
#             SUM(Enrollment) from CS1172Data where
#             NUMBER = "%s" 

#             ''' % (num)

#             cur.execute(executeString)

#             for val in cur:
#                 taken = val[0]

#             avail = offered - taken
#             availStr = str(avail)

#             #string = "There are " + str(three) + "seats available in course " + num
#             string = "There are {0} seats available in course {1}".format(availStr, num)

#             speech_output += string
#             reprompt_text = ""

#         cur.close()
#         conn.close()

#     return build_response(session_attributes, build_speechlet_response(
#         card_title, speech_output, reprompt_text, should_end_session))

