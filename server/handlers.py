import json
import logging

from resolvers import resolve
from middlewares import (
    compression_middleware, encryption_middleware
)
from protocol import (
    validate_request, make_response
)


@compression_middleware
@encryption_middleware
def handle_default_request(raw_request):
    request = json.loads(raw_request.decode())

    if validate_request(request):
        action_name = request.get('action')
        controller = resolve(action_name)
        if controller:
            try:
                logging.debug(f'Controller {action_name} resolved with request: {request}')
                response = controller(request)
            except Exception as err:
                logging.critical(f'Controller {action_name} error: {err}')
                response = make_response(request, 500, 'Internal server error')
        else:
            logging.error(f'Controller {action_name} not found')
            response = make_response(request, 404, f'Action with name {action_name} not supported')
    else:
        logging.error(f'Controller wrong request: {request}')
        response = make_response(request, 400, 'wrong request format')

    return json.dumps(response).encode()