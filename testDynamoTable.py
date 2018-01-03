import boto3

from dynamoClient import DynamoClient


# dynamodb = boto3.resource('dynamodb', region_name='us-east-1', endpoint_url="http://localhost:8000")

# table = dynamodb.create_table(
#     TableName='test',
#     KeySchema=[
#         {
#             'AttributeName': 'uid',
#             'KeyType': 'HASH'  #Partition key
#         }
#     ],
#     AttributeDefinitions=[
#         {
#             'AttributeName': 'uid',
#             'AttributeType': 'S'  #Partition key
#         }
#     ],
#     ProvisionedThroughput={
#         'ReadCapacityUnits': 10,
#         'WriteCapacityUnits': 10
#     }
# )
# client = boto3.client('dynamodb')

# # dynamodb = boto3.resource('dynamodb',endpoint_url="https://dynamodb.us-east-1.amazonaws.com") 

# client.update_item(TableName="TranslocatorUserInfo", 
# 	Item={
#                     'uid': 123, #pk
#                     'agency_id': "abcd",
#                     'stop_id': 653,
#                     'stop_name': "poled"
#                 }
#                )


dynamoClient = DynamoClient("TranslocatorUserInfo")


dynamoClient.store_agency_route_stop("ABC", 123, 456, 789)
success, info = dynamoClient.get_route_info("ABC")
print info['stop_name']
print dynamoClient.get_route_info("AB")

    
           