import urllib2
import json
import unirest
#for dynamoDB
from dynamoClient import DynamoClient
#transloc API
from translocController import TranslocController
########################## Globals ##################################

tableName = "TranslocatorUserInfo"
first_session = True
mySkillId = "amzn1.ask.skill.b9945778-9da9-4879-a534-97309608acae"
dynamo_table_key = ""

translocController = TranslocController()
dynamoClient = DynamoClient(tableName)
####################################################################

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
    is_welcome_message = True
    return get_welcome_response(is_welcome_message)

def on_intent(intent_request, session):
    intent = intent_request["intent"]
    intent_name = intent_request["intent"]["name"]

    global dynamo_table_key
    dynamo_table_key = session["user"]["userId"]

    #check and or set first session could just make a function to catch the except.
    #make this get(uid) if error, then we have to setup, otherwise, were fine

    if intent_name == "GetNearestBus":
        query_success, user_info = dynamoClient.get_route_info(dynamo_table_key)
        if query_success:
            translocController.set_agency_id(user_info['agency_id'])
            translocController.set_stop_id(user_info['stop_id'])
        return get_nearest_bus(intent)
    elif intent_name == "ConfigureLocation":
        return configure_location(intent)
    elif intent_name == "GetOption":
        return get_option(intent)
    elif intent_name == "AMAZON.HelpIntent":
        query_success, user_info = dynamoClient.get_route_info(dynamo_table_key)
        if query_success:
            global first_session
            first_session = False
        is_welcome_message = False
        return get_welcome_response(is_welcome_message)
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
    print speech_output
    return build_response({}, build_speechlet_response(card_title, speech_output, None, should_end_session))

def get_nearest_bus(intent):
    session_attributes = {}
    card_title = "Transloc nearest bus time"
    speech_output = "You're trying to get a bus time. Awesome."
    reprompt_text = "I'm not sure what you're asking for."
    should_end_session = True 

    #Transloc 
    agency_id = translocController.get_agency_id()
    stop_id = translocController.get_stop_id() 
    
    #Make sure everything is configured
    if(agency_id == -1 or stop_id == -1):
        speech_output = "You must configure your location before we can find your stop and bus times."
        return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

    #sample data
    # min_till_bus = translocController.get_next_bus_arrival(347, 4123822)
    min_till_bus = translocController.get_next_bus_arrival(agency_id, stop_id)
    if min_till_bus == -1:
        speech_output = "Transloc buses are not running at this time."
    elif min_till_bus == -99:
        speech_output = "An error occurred calling the Transloc API. Please report this to mcr5fh@virginia.edu."
    else: 
        speech_output = "The next bus is in " + str(min_till_bus) + " minutes"

    print speech_output
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
        stop_list = translocController.set_closest_stop(addr)
        if(len(stop_list) > 1):
            #set list in controller
            translocController.set_getting_options(True)

            speech_output = "The following stops are available in your area: "
            for index, val in enumerate(stop_list):
                speech_output += "Option " + str(index + 1) + ": " + val + ", "

            speech_output = speech_output[:-2]
            speech_output += ". Select the desired option by saying 'option' followed by the corresponding number."

        elif len(stop_list) == 1:
            #speech_output = "The address you provided is " + addr
            speech_output = "Your stop is now set to " + stop_list[0]
        else: 
            speech_output = "There were no bus stops found near your location. Make sure Transloc has bus stops near you."
            should_end_session = True
    
    print speech_output

    return build_response(session_attributes, build_speechlet_response(
    card_title, speech_output, reprompt_text, should_end_session))

def get_option(intent):
    session_attributes = {}
    card_title = "Translocator get option"
    speech_output = "This was not a valid option. Please try again."
    reprompt_text = "Please provide a valid option."
    should_end_session = True

    if translocController.get_getting_options() == False:
        speech_output = "Please start by using the keyword configure."

        return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))    

    if "option" in intent["slots"]:
        try:
            speech_output = "option is a slot."
            option = intent["slots"]["option"]["value"]
            option = int(option)
            stop_list = translocController.get_closest_stop_list()
    #       speech_output += " stop_list is " + str(len(stop_list)) + "entries long. provided option: " + option
            if option <= len(stop_list):
                #need the minus ones for indexing
                stop_name = stop_list[option-1]
                translocController.set_stop_id_from_stop_list(option-1)

                speech_output = "You chose option " + str(option) + ": " + stop_name

                #store the location data
                if not dynamoClient.store_agency_route_stop(dynamo_table_key, translocController.get_agency_id(), 
                    translocController.get_stop_id(), stop_name):
                    speech_output = "There was an error choosing the option: " + stop_name
        except Exception as e:
            speech_output = "There was an error choosing your option. Please try configuring your locaion again."
            print "Error in Get Option"
            print e
    
    print speech_output

    return build_response(session_attributes, build_speechlet_response(
    card_title, speech_output, reprompt_text, should_end_session))    


def get_welcome_response(is_welcome_message):
    session_attributes = {}
    card_title = "Translocator"
    speech_output = ""
    if is_welcome_message:
        speech_output += "Welcome to the Translocator skill. "

    if first_session:
        speech_output += "Configure your device's location using the " \
        "'configure' keyword, followed by your address."
    else:
        speech_output += "Get the next bus arrival time to your local stop " \
        "by saying 'get the next bus time'."

    reprompt_text = "You can ask when the next bus is coming to your nearest stop." \
                    "You can also configure your device's location by saying configure followed by your address."
    should_end_session = False
    print speech_output

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
        "version": "1.1",
        "sessionAttributes": session_attributes,
        "response": speechlet_response
    }
