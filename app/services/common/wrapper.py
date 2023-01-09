import datetime
import uuid


class ResponseWrapper:

    @staticmethod
    def wrap_json(json_response):
        base_response = {
            'timestamp': datetime.datetime.now(),
            'uuid': uuid.uuid4(),
            'payload': json_response
        }

        return base_response
