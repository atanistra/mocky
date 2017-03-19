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
    def __init__(self, responses_path):
        self._responses_path = responses_path

    def get(self):
        self._save_request(request)
        response = self._get_response(MethodFile.GET.value)
        return response

    def post(self):
        self._save_request(request)
        response = self._get_response(MethodFile.POST.value)
        return response

    def put(self):
        self._save_request(request)
        response = self._get_response(MethodFile.POST.value)
        return response

    def delete(self):
        self._save_request(request)
        response = self._get_response(MethodFile.POST.value)
        return response

    def _get_response(self, file_name):
        file_path = os.path.join(self._responses_path, file_name)
        try:
            response_data = self._load_response(file_path)
        except IOError:
            response_data = ENDPOINT_NOT_ALLOWED_RESPONSE
        body = response_data.get('body')
        code = response_data.get('status')
        headers = response_data.get('headers')
        response = Response(json.dumps(body), code, headers)
        return response

    def _save_request(self, request):
        pass

    def _load_response(self, file_path):
        with open(file_path) as f:
            response = json.load(f)
        return response


class ResourceRegistrator:
    def __init__(self, endpoints_configuration_file, responses_dir):
        self._endpoints = endpoints_configuration_file
        self._responses_dir = responses_dir

    def register(self):
        endpoints = self._read_endpoints_file()
        for endpoint in endpoints:
            responses_path = os.path.join(self._responses_dir, endpoint[1:])
            api.add_resource(FileResource, endpoint, resource_class_kwargs={"responses_path": responses_path})

    def _read_endpoints_file(self):
        with open(self._endpoints) as f:
            endpoints_data = json.load(f)
        return endpoints_data


if __name__ == '__main__':
    config = Config()
    app = Flask(__name__)
    api = Api(app)
    rr = ResourceRegistrator(config.endpoints_file, config.responses_dir)
    rr.register()
    app.run(debug=True, host="0.0.0.0", port=config.mock_port)
