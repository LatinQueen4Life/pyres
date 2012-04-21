#!/usr/bin/env python

import optparse
from collections import defaultdict

import redis
from flask import Flask, request, render_template, redirect
from gevent import pywsgi
from pyres import failure
from pyres import ResQ

app = Flask(__name__)
app.debug = True

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


@app.route('/failed')
def get_failed():
    start = int(request.args.get("start", 0))
    limit = int(request.args.get("limit", 250))
    jobs = []
    for resq in RESQUES:
        for job in failure.all(resq, start, start+limit):
            backtrace = job['backtrace']

            if isinstance(backtrace, list):
                backtrace = '\n'.join(backtrace)

            item = job
            item['failed_at'] = job['failed_at']
            item['worker'] = job['worker']
            item['payload_args'] = str(job['payload']['args'])[:1024]
            item['payload_class'] = job['payload']['class']
            item['traceback'] = backtrace
            jobs.append(item)

    return render_template("failures.html", jobs=jobs, dsn=DSN, limit=limit)


@app.route('/failed/delete_all')
def delete_all_failed():
    for resq in RESQUES:
        resq.redis.rename('resque:failed','resque:failed-staging')
        resq.redis.delete('resque:failed-staging')
    raise redirect('/failed/')


@app.route('/queues/<queue_id>')
def get_items_in_queue(queue_id):
    if queue_id == "failed":
        return redirect("/failed")
    start = int(request.args.get("start", 0))
    limit = int(request.args.get("limit", 250))
    jobs = []
    for resq in RESQUES:
        for job in resq.peek(queue_id, start, start+limit):
            jobs.append({
                'class':job['class'],
                'args': str(job['args'])
            })
    return render_template("queues.html", queue=queue_id, jobs=jobs, dsn=DSN, 
                           start=start, end=start+limit)

@app.route('/stats')
def get_stats():
    queue_stats = defaultdict(int)
    queue_stats['queues'] = RESQUES[0].redis.scard("resque:queues")
    queue_stats["servers"] = DSN
    for resq in RESQUES:
        queue_stats["processed"] += int(resq.redis.get("resque:stat:processed"))
        queue_stats["failed"] += int(resq.redis.get("resque:stat:failed"))
    return render_template("stats.html", data=queue_stats, dsn=DSN)

def main(host, port, dsn):
    if not dsn:
        raise Exception("Please enter redis server to poll on")
    port = int(port)
    global DSN
    DSN = dsn
    dsn = dsn.split(",")
    for host_port in dsn:
        rhost, rport = host_port.split(":")
        global RESQUES
        RESQUES.append(ResQ(redis.Redis(host=rhost, port=int(rport))))

    print "server up on %d" %port
    pywsgi.WSGIServer((host, port), app).serve_forever()


