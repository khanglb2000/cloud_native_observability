from flask import Flask, render_template, jsonify, request
import threading
import requests
import random
import time
from prometheus_flask_exporter import PrometheusMetrics
import logging
from jaeger_client import Config

app = Flask(__name__)
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
endpoints = ('error', 'foo', 'healthz')

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

tracer = init_tracer('frontend')

def random_endpoint():
    while True:
        try:
            target = random.choice(endpoints)
            requests.get("http://app:8081/%s" % target, timeout=1)

        except:
            pass

@app.route('/')
@by_endpoint_counter
def homepage():
    return render_template("main.html")
    with tracer.start_span('random_endpoint') as span:
        threading.Thread(target=random_endpoint).start()
        for _ in range(4):
            thread = threading.Thread(target=random_endpoint)
            thread.daemon = True
            thread.start()

        while True:
            time.sleep(1)
    


@app.route('/healthz')
@by_endpoint_counter
def healthcheck():
    app.logger.info('Status request successfull')
    return jsonify({"result": "OK - healthy"})

if __name__ == "__main__":    
    app.run()