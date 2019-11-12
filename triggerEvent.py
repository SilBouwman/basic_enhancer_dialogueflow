# Payload
payload = {
  "responseId": "5b2333a1-77c2-4935-a0e4-6cf658d15588-b81332aa",
  "queryResult": {
    "queryText": "triggerEvent aub",
    "action": "triggerEvent",
    "parameters": {},
    "allRequiredParamsPresent": "true",
    "fulfillmentMessages": [
      {
        "payload": {
    "logic": {
        "defaultEvent": "afsluitenEvent",
        "cases": [
            {
                "event": "buitenlandFlow",
                "operator": "And",
                "operations": [
                    {
                        "operator": "NotEquals",
                        "comparisonValue": "NL",
                        "actualValue": "NL"
                    }
                ]
            },
            {
                "event": "socialEvent",
                "operator": "Or",
                "operations": [
                    {
                        "operator": "Equals",
                        "comparisonValue": "Twitter",
                        "actualValue": "$kanaal"
                    },
                    {
                        "operator": "Equals",
                        "comparisonValue": "Facebook",
                        "actualValue": "$kanaal"
                    }
                ]
            },
            {
                "event": "vraagTelefoonnummerEvent",
                "operator": "And",
                "operations": [
                    {
                        "operator": "Equals",
                        "comparisonValue": "",
                        "actualValue": "$mobielNummer"
                    },
                    {
                        "operator": "Equals",
                        "comparisonValue": "",
                        "actualValue": "$vastNummer"
                    }
                ]
            },
            {
                "event": "postalCodeValid",
                "operator": "And",
                "operations": [
                    {
                        "operator": "Match",
                        "comparisonValue": "^[1-9][0-9]{3}(?:[a-zA-Z]{2})?$",
                        "actualValue": "4317NJJ"
                    }
                ]
            },
            {
                "event": "postalCodeInvalid",
                "operator": "And",
                "operations": [
                    {
                        "operator": "NotMatch",
                        "comparisonValue": "^[1-9][0-9]{3}(?:[a-zA-Z]{2})?$",
                        "actualValue": "4812th"
                    }
                ]
            },
            {
                "event": "datumEvent",
                "operator": "And",
                "operations": [
                    {
                        "operator": "dateGreaterThan",
                        "comparisonValue": "2019-08-25T12:00:00+02:00",
                        "actualValue": "2019-08-25T12:00:00+02:00"
                    }
                ]
            }
        ]
    }
}
      }
    ],
    "intent": {
      "name": "projects/meastro-dev-sil-kegqgs/agent/intents/fad3719d-3ac1-4101-9397-88169cf4370e",
      "displayName": "test_triggerEvent"
    },
    "intentDetectionConfidence": 1,
    "languageCode": "nl"
  },
  "originalDetectIntentRequest": {
    "payload": {}
  },
  "session": "projects/meastro-dev-sil-kegqgs/agent/sessions/fb955289-a058-9ffd-2bce-c5cadbdc5078"
}

# Desired output
output = {
    "followupEventInput": {
        "languageCode": "nl",
        "name": "VALUE"
    }
}

# Function for converting time
def convert_time(datetime_string):
    """Converts a timestamp string with the format %Y-%m-%dT%H:%M:%S%z to a datetime object.

       Args:
         datetime_string: a timestamp string with the format %Y-%m-%dT%H:%M:%S%z.

       Returns:
         Datetime object.

       Raises:
         Value error: If the format is not %Y-%m-%dT%H:%M:%S%z.
       """
    import datetime
    try:
        return datetime.datetime.strptime(datetime_string[:-6], '%Y-%m-%dT%H:%M:%S')
    except:
        raise ValueError(f'Does not know this type of timestamp, please use %Y-%m-%dT%H:%M:%S%z as timestamp format')


# Cloud function
import re
op = {'And': lambda x, y: x and y,
      'Or': lambda x, y: x or y,
      'greaterThan': lambda x, y: x > y,
      "NotEquals": lambda x, y: x != y,
      "Equals": lambda x, y: x == y,
      "Match": lambda x, y: re.match(x, y),  # Valid code for regex for dutch postal codes: "^[1-9][0-9]{3}(?:[a-zA-Z]{2})?$"
      "NotMatch": lambda x, y: not re.match(x, y),
      "dateGreaterThan": lambda x, y: convert_time(x) > convert_time(y)
      }


def formatting(value):
    """Formats a value in json response object.

       Args:
         value: a string to return to dialogue flow.

       Returns:
         json response
    """
    import json
    # Formatting the output
    output = {
        "followupEventInput": {
            "languageCode": "nl",
            "name": value
        }
    }
    return json.dumps(output), 200, {'ContentType': 'application/json'}


def requestHandler(request):
    """Handles all the logic from a json request of dialogue flow.

       Args:
         request: a api post request.

       Returns:
         json response

       Raises:
         Value error: If it does not recognize the type of high over operator.
         Value error: If it does not recognize the type of operator.
    """
    request_json = request.get_json()
    request_json = request_json["queryResult"]["fulfillmentMessages"][0]["payload"]

    # Checking if the json has a standard event
    if "logic" not in request_json:
        VALUE = request_json["event"]
        return formatting(VALUE)

    # Checking for cases
    json_logic = request_json["logic"]
    for case in json_logic["cases"]:
        op_highover = {"Or": False, "And": True}

        # Checking operations
        operations = case["operations"]
        high_over_operator = case["operator"]
        if high_over_operator not in op_highover:
            raise ValueError(f'Does not know this type of operator: {high_over_operator}')

        # Check if one of the operations is true and appending that to orResult and andResult
        for operation in operations:
            if operation["operator"] not in op:
                raise ValueError(f'Does not know this type of operator: {operation["operator"]}')

            value_bool = op[operation["operator"]](operation["comparisonValue"], operation["actualValue"])
            op_highover["Or"] = op_highover["Or"] or value_bool
            op_highover["And"] = op_highover["And"] and value_bool

        # Return if one of the conditions is met
        if op_highover[high_over_operator]:
            VALUE = case["event"]
            return formatting(VALUE)

    # Case is not found so return default value
    VALUE = json_logic["defaultEvent"]
    return formatting(VALUE)


# Flask function for testing, Emulator
if __name__ == "__main__":
    from flask import Flask, request

    app = Flask(__name__)


    @app.route("/eventTrigger", methods=["POST"])
    def eventTrigger():
        return requestHandler(request)


    app.run(port=5000, debug=True)
