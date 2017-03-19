from flask import Flask, request, Response
from flask_restful import Resource, Api
import os
import json

app = Flask(__name__)
api = Api(app)

class Endpoint(Resource):
    def __init__(self, responses_path):
        self._responses_path = responses_path

    def get(self):
        self._save_request(request)
        response = self._resolve("get.json")
        return response

    def post(self):
        pass

    def put(self):
        pass

    def delete(self):
        pass

    def _resolve(self, file_name):
        file_path = os.path.join(self._responses_path, file_name)
        print(file_path)
        try:
            response_data = self._load_response(file_path)
            body = response_data.get('body')
            code = response_data.get('status')
            headers = response_data.get('headers')
            response = Response(json.dumps(body), code, headers)

        except IOError:
            response = {"messahe": "dupa"}
        return response

    def _save_request(self, request):
        pass

    def _load_response(self, file_path):
        with open(file_path) as f:
            response = json.load(f)
        return response

class ResourceRegistrator:
    def __init__(self, config):
        self._endpoints = config.endpoints_file
        self._responses_dir = config.responses_dir

    def _resolve_paths(self, methods, response_dir):
        paths = {}
        for method in methods:
            paths[method] = os.path.join(self._responses_dir, response_dir, method + ".json")
        return paths

    def register(self):
        endpoints = self._read_endpoints_file()
        for endpoint in endpoints:
            e_dir = endpoint['response_dir']
            e_path = endpoint['path']
            responses_path = os.path.join(self._responses_dir, e_dir)
            api.add_resource(Endpoint, e_path, resource_class_kwargs={"responses_path": responses_path})

    def _read_endpoints_file(self):
        with open(self._endpoints) as f:
            endpoints_data = json.load(f)
        return endpoints_data


class Config:
    endpoints_file = os.getenv("MOCK_ENDPOINTS", "endpoints.json")
    responses_dir = os.getenv("MOCK_RESPONSES_DIR", "responses")

if __name__ == '__main__':
    config = Config()
    rr = ResourceRegistrator(config)
    rr.register()
    app.run(debug=True, host="0.0.0.0")
