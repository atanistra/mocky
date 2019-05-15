import os
import json
import time
import sys
from base64 import b64decode
from enum import Enum

from flask import Flask, request, Response
from flask_restful import Resource, Api

METHOD_NOT_ALLOWED_RESPONSE = {
    'body': {'message': 'Method not implemented'},
    'headers': {'Content-Type': 'application/json'},
    'status_code': 405
}

PREFLIGHT_RESPONSE = {
    'headers': {'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, GET, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': '*',
                'Access-Control-Max-Age': '86400'},
    'status_code': 200
}


def load_json(file_path):
    with open(file_path) as f:
        data = json.load(f)
    return data


def save_json(file_path, data):
    with open(file_path, 'w+') as f:
        json.dump(data, f)


class MethodFile(Enum):
    GET = 'get.json'
    POST = 'post.json'
    PUT = 'put.json'
    DELETE = 'delete.json'
    OPTIONS = 'options.json'
    PATCH = 'patch.json'


class Config:
    def __init__(self):
        mock_workdir = os.getenv('MOCK_WORKDIR')
        timeout = os.getenv('MOCK_TIMEOUT', 0)
        mock_endpoints = os.getenv('MOCK_ENDPOINTS', 'endpoints.json')
        responses_dir_name = os.getenv('MOCK_RESPONSES_DIR_NAME', 'responses')

        self.mock_port = int(os.getenv('MOCK_PORT', 8080))
        self.endpoints_file = os.path.join(mock_workdir, mock_endpoints)
        self.responses_dir = os.path.join(mock_workdir, responses_dir_name)
        self.timeout = int(timeout)


class FileResource(Resource):
    _response_file_path = None
    _request_data = None
    _response = None
    _method = None
    _method_file = None

    def __init__(self, responses_path, endpoint_path, timeout):
        self._responses_path = responses_path
        self._last_request_file_path = os.path.join(self._responses_path, 'last_request.json')
        self._all_requests_file_path = os.path.join(self._responses_path, 'all_request.log')
        self._endpoint_path = endpoint_path
        self._timeout = timeout

    def get(self, **kwargs):
        self._process(**kwargs)
        return self._response

    def post(self, **kwargs):
        self._process(**kwargs)
        return self._response

    def put(self, **kwargs):
        self._process(**kwargs)
        return self._response

    def delete(self, **kwargs):
        self._process(**kwargs)
        return self._response

    def options(self, **kwargs):
        self._process(**kwargs)
        return self._response

    def patch(self, **kwargs):
        self._process(**kwargs)
        return self._response

    def _process(self, **kwargs):
        self._process_request(**kwargs)
        self._response = self._get_response()

    def _process_request(self, **kwargs):
        self._method = request.method
        self._method_file = MethodFile[self._method].value
        self._extract_request_data()
        self._update_file_paths(**kwargs)
        self._log_request_data()
        self._save_request_data()
        self._update_requests_log_file()

    def _extract_request_data(self):
        request_data = {
            'headers': dict(request.headers),
            'body': request.json if request.is_json else request.data.decode() or None,
            'args': dict(request.args),
            'endpoint': request.endpoint,
            'method': self._method
        }
        self._request_data = request_data

    def _save_request_data(self):
        try:
            save_json(self._last_request_file_path, self._request_data)
        except Exception as ex:
            app.logger.error('Unable to save request:\nPath: %s\nResponse:\n%s\nException:\n%s\n%s ' % (
                self._last_request_file_path, self._request_data, ex, sys.exc_info()[0]))

    def _update_requests_log_file(self):
        dumped_requests = json.dumps(self._request_data)
        with open(self._all_requests_file_path, 'a+') as f:
            f.writelines(f'{dumped_requests}\n')

    def _log_request_data(self):
        app.logger.info("REQUEST: %s" % (self._request_data,))

    def _update_file_paths(self, **kwargs):
        endpoint_path = self._endpoint_path

        for key, value in kwargs.items():
            path_key = '<%s>' % key
            if key.startswith('__'):
                endpoint_path = endpoint_path.replace(path_key, key)
            else:
                endpoint_path = endpoint_path.replace(path_key, value)

        self._response_file_path = os.path.join(self._responses_path, endpoint_path, self._method_file)

    def _get_response(self):
        end = time.time() + self._timeout
        app.logger.info('Trying to load response from: %s' % (self._response_file_path,))
        while True:
            try:
                response_data = load_json(self._response_file_path)
                break
            except IOError:
                if self._method_file == MethodFile.OPTIONS.value:

                    response_data = PREFLIGHT_RESPONSE
                    break
                elif time.time() > end:
                    app.logger.warn('Response not found!')
                    response_data = METHOD_NOT_ALLOWED_RESPONSE
                    break
                else:
                    time.sleep(0.1)

        body = response_data.get('body')
        status_code = response_data.get('status_code')
        headers = response_data.get('headers')
        app.logger.info("RESPONSE: %s" % (response_data,))
        if headers and headers.get('Content-Type') == 'application/json':
            body = json.dumps(body)
        if headers and headers.get('Content-Type').startswith('image'):
            body = b64decode(body.encode())
        else:
            body = body.encode()
        response = Response(body, status_code, headers)
        return response


if __name__ == '__main__':

    config = Config()

    app = Flask(__name__)
    api = Api(app)

    resources = load_json(config.endpoints_file)
    for resource in resources:
        api.add_resource(FileResource, resource, endpoint=resource,
                         resource_class_kwargs={'responses_path': config.responses_dir,
                                                'endpoint_path': resource[1:], 'timeout': config.timeout})

    app.run(debug=True, host='0.0.0.0', port=config.mock_port)
