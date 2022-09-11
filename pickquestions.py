import requests
import json
import pprint
from json2html import *

API_KEY = "1016~EPKReqgq2lC2ugrK2J7O5yHOuLPDq5mE9ZcZ645p271EVf4UMD7jE38l7tvkG3Sa"
API_URL = "https://ufl.instructure.com/api/v1/courses/460732/quizzes/1132161/groups/774485"

token_header = {'Authorization': f'Bearer {API_KEY}'}
response = requests.get(API_URL, headers=token_header)
obj = response.json()

pprint.pprint(obj)

# with open("right.json", "w") as outfile:
#     json.dump(obj, outfile, indent=4)
