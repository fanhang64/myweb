import json
import time
import decimal
from datetime import date, datetime

from flask import Response


class JsonResponseEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.strftime('%Y-%m-%d %H:%M:%S')
        if isinstance(o, date):
            return o.strftime('%Y-%m-%d')
        if isinstance(o, time):
            return o.strftime('%H:%M:%S')
        if isinstance(o, bytes):
            return o.decode('utf-8')
        if isinstance(o, decimal.Decimal):
            return float(o)

        return json.JSONEncoder.default(self, o)


class JsonResponse:
    def __init__(self, data):
        code = 0
        msg = 'ok'
        if isinstance(data, dict):
            code = data.pop('code', code)
            msg = data.pop('msg', msg)

        self.data = {
            'errcode': code,
            'errmsg': msg,
        }
        if data:
            self.data['data'] = data

    def to_response(self):
        return Response(
            response=json.dumps(self.data, cls=JsonResponseEncoder),
            status=200,
            mimetype='application/json'
        )
