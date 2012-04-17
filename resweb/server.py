#!/usr/bin/env python

import optparse
from collections import defaultdict

import redis
from flask import Flask, request, render_template
from gevent import pywsgi
from pyres import failure
from pyres import ResQ

app = Flask(__name__)

RESQUES = []
DSN = ""

@app.route('/')
def home():
    queue_stats = defaultdict(int)
    queues = RESQUES[0].queues()
    for resq in RESQUES:
        for q in queues:
            queue_stats[q] += resq.size(q)
        queue_stats["failed"] += failure.count(resq)
    return render_template("index.html", queue_stats=queue_stats, dsn=DSN)


def get_cmd_line_options():
    """Return an Options object with the command line options.
    """
    parser = optparse.OptionParser()
    parser.add_option("--redis", dest="redis", action="store",
            help="List of redis servers.")
    parser.add_option("--port", dest="port", action="store",
            help="Port to listen.")
    (options, args) = parser.parse_args()
    return options, args

def main():
    opts, args = get_cmd_line_options()
    port = 8000
    if opts.redis:
        global DSN
        DSN = opts.redis
        dsn = opts.redis.split(",")
        for host_port in dsn:
            host, port = host_port.split(":")
            global RESQUES
            RESQUES.append(ResQ(redis.Redis(host=host, port=int(port))))

    if opts.port:
        port = int(opts.port)
    print "server up on %d" %port
    pywsgi.WSGIServer(("0.0.0.0", port), app).serve_forever()

if __name__ == "__main__":
    main()

