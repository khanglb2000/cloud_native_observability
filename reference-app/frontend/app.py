from flask import Flask, render_template, jsonify, request
import threading
import requests
import random
import time
import os
from prometheus_flask_exporter import PrometheusMetrics
import logging
from jaeger_client import Config

app = Flask(__name__)

#https://github.com/rycus86/prometheus_flask_exporter#prometheus-flask-exporter
metrics = PrometheusMetrics(app, group_by='endpoint')

# static information as metric
metrics.info('app_info', 'Application info', version='1.0.3')
metrics.register_default(
    metrics.counter(
        'by_path_counter', 'Request count by request paths',
        labels={'path': lambda: request.path}
    )
)

by_endpoint_counter = metrics.counter(
    'by_endpoint_counter', 'Request count by request endpoint',
    labels={'endpoint': lambda: request.endpoint}
)

def init_tracer(service):
    logging.getLogger('').handlers = []
    logging.basicConfig(format='%(message)s', level=logging.DEBUG)

    config = Config(
        config={
            'sampler': {
                'type': 'const',
                'param': 1,
            },
            'logging': True,
        },
        service_name=service,
    )

    # this call also sets opentracing.tracer
    return config.initialize_tracer()

tracer = init_tracer('frontend-app')

endpoints = ('api', 'error_410', 'error_500', 'star', 'healthz')

def gen_backend_events():
    try:
        target = random.choice(endpoints)
        backend_service = os.environ.get('BACKEND_ENDPOINT', default="https://localhost:8081")
        url_endpoint= f'{backend_service}/'+"%s" %target
        backend_response = requests.get(url_endpoint, timeout=1)
        return "OK"
    except:
        pass

@app.route('/')
@by_endpoint_counter
def homepage():
    with tracer.start_span('gen_backend_events') as span:
        for _ in range(2):
            gen_backend_events

    return render_template("main.html")
  

@app.route('/healthz')
@by_endpoint_counter
def healthcheck():
    app.logger.info('Status request successfull')
    return jsonify({"result": "OK - healthy"})

if __name__ == "__main__":    
    app.run()