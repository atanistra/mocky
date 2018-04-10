import os
import json
from enum import Enum

from flask import Flask, request, Response
from flask_restful import Resource, Api

METHOD_NOT_ALLOWED_RESPONSE = {
    'body': {'message': 'Method not implemented'},
    'headers': {'Content-Type': 'application/json'},
    'status': 405
}


def load_json(file_path):
    with open(file_path) as f:
        data = json.load(f)
    return data


def save_json(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f)


class MethodFile(Enum):
    GET = 'get.json'
    POST = 'post.json'
    PUT = 'put.json'
    DELETE = 'delete.json'


class Config:
    def __init__(self):
        mock_workdir = os.getenv('MOCK_WORKDIR')
        mock_endpoints = os.getenv('MOCK_ENDPOINTS', 'endpoints.json')
        responses_dir_name = os.getenv('MOCK_RESPONSES_DIR_NAME', 'responses')

        self.mock_port = int(os.getenv('MOCK_PORT', 8080))
        self.endpoints_file = os.path.join(mock_workdir, mock_endpoints)
        self.responses_dir = os.path.join(mock_workdir, responses_dir_name)


class FileResource(Resource):
    _response_file_path = None

    def __init__(self, responses_path, endpoint_path):
        self._responses_path = responses_path
        self._endpoint_path = endpoint_path

    def get(self, **kwargs):
        self._update_file_paths(MethodFile.GET, **kwargs)
        self._save_request_data()
        response = self._get_response()
        return response

    def post(self, **kwargs):
        self._update_file_paths(MethodFile.POST, **kwargs)
        self._save_request_data()
        response = self._get_response()
        return response

    def put(self, **kwargs):
        self._update_file_paths(MethodFile.PUT, **kwargs)
        response = self._get_response()
        return response

    def delete(self, **kwargs):
        self._update_file_paths(MethodFile.DELETE, **kwargs)
        response = self._get_response()
        return response

    def _save_request_data(self):
        request_data = {
            'headers': dict(request.headers),
            'body': request.json if request.is_json else request.data.decode() or None,
            'args': dict(request.args),
            'endpoint': request.endpoint,
            'method': request.method
        }
        save_json(self._request_file_path, request_data)

    def _update_file_paths(self, method, **kwargs):
        endpoint_path = self._endpoint_path

        for key, value in kwargs.items():
            path_key = '<%s>' % key
            if key.startswith('__'):
                endpoint_path = endpoint_path.replace(path_key, key)
            else:
                endpoint_path = endpoint_path.replace(path_key, value)

        self._response_file_path = os.path.join(self._responses_path, endpoint_path, method.value)
        self._request_file_path = os.path.join(self._responses_path, 'last_request.json')

    def _get_response(self):
        try:
            response_data = load_json(self._response_file_path)
        except IOError:
            response_data = METHOD_NOT_ALLOWED_RESPONSE
        body = response_data.get('body')
        status_code = response_data.get('status_code')
        headers = response_data.get('headers')
        response = Response(json.dumps(body), status_code, headers)
        return response


if __name__ == '__main__':

    config = Config()

    app = Flask(__name__)
    api = Api(app)

    resources = load_json(config.endpoints_file)
    for resource in resources:
        api.add_resource(FileResource, resource, endpoint=resource,
                         resource_class_kwargs={'responses_path': config.responses_dir,
                                                'endpoint_path': resource[1:]})

    app.run(debug=True, host='0.0.0.0', port=config.mock_port)
