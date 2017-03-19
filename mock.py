from enum import Enum

from flask import Flask, request, Response
from flask_restful import Resource, Api
import os
import json

ENDPOINT_NOT_ALLOWED_RESPONSE = {
    "body": {"message": "Method not implemented"},
    "headers": {"Content-Type": "application/json"},
    "status": 405
}


def load_json(file_path):
    with open(file_path) as f:
        data = json.load(f)
    return data


class MethodFile(Enum):
    GET = "get.json"
    POST = "post.json"
    PUT = "put.json"
    DELETE = "delete.json"


class Config:
    def __init__(self):
        endpoints_file = os.getenv("MOCK_ENDPOINTS", "endpoints.json")
        responses_dir = os.getenv("MOCK_RESPONSES_DIR", "responses")
        self.endpoints_file = self._update_path(endpoints_file)
        self.responses_dir = self._update_path(responses_dir)
        self.mock_port = int(os.getenv("MOCK_PORT", 8080))

    @staticmethod
    def _update_path(path):
        work_dir = os.path.dirname(os.path.realpath(__file__))
        return os.path.join(work_dir, path)


class FileResource(Resource):
    def __init__(self, responses_path, endpoint_path):
        self._responses_path = responses_path
        self._endpoint_path = endpoint_path

    def get(self):
        self._save_request(request)
        response = self._get_response(MethodFile.GET)
        return response

    def post(self):
        self._save_request(request)
        response = self._get_response(MethodFile.POST)
        return response

    def put(self):
        self._save_request(request)
        response = self._get_response(MethodFile.PUT)
        return response

    def delete(self):
        self._save_request(request)
        response = self._get_response(MethodFile.DELETE)
        return response

    def _get_response(self, file_name):
        file_path = os.path.join(self._responses_path, self._endpoint_path, file_name.value)
        try:
            response_data = load_json(file_path)
        except IOError:
            response_data = ENDPOINT_NOT_ALLOWED_RESPONSE
        body = response_data.get('body')
        code = response_data.get('status')
        headers = response_data.get('headers')
        response = Response(json.dumps(body), code, headers)
        return response

    def _save_request(self, request):
        pass


if __name__ == '__main__':

    config = Config()

    app = Flask(__name__)
    api = Api(app)

    resources = load_json(config.endpoints_file)

    for resource in resources:
        api.add_resource(FileResource, resource, resource_class_kwargs={"responses_path": config.responses_dir,
                                                                        "endpoint_path": resource[1:]})

    app.run(debug=True, host="0.0.0.0", port=config.mock_port)
