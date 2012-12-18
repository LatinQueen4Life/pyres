import logging

from optparse import OptionParser

from resweb import server
from pyres.horde import Khan
from pyres import setup_logging
from pyres.scheduler import Scheduler
from resweb import server as resweb_server
from pyres.worker import Worker


def pyres_manager():
    usage = "usage: %prog [options] arg1"
    parser = OptionParser(usage=usage)
    #parser.add_option("-q", dest="queue_list")
    parser.add_option("--host", dest="host", default="localhost")
    parser.add_option("--port",dest="port",type="int", default=6379)
    parser.add_option('-l', '--log-level', dest='log_level', default='info', help='log level.  Valid values are "debug", "info", "warning", "error", "critical", in decreasing order of verbosity. Defaults to "info" if parameter not specified.')
    parser.add_option("--pool", type="int", dest="pool_size", default=1, help="Number of minions to spawn under the manager.")
    parser.add_option('-f', dest='logfile', help='If present, a logfile will be used.')
    parser.add_option("-n", "--nonblocking-pop", dest="blocking_pop", action="store_false", default=True, help="If absent, Pyres will use the Redis blocking pop (BLPOP) to obtain jobs from the queue(s). If present, Redis will use a non-blocking pop (LPOP) and will sleep for up to 8 seconds if no jobs are available.")
    parser.add_option(
        "-r", "--reinit-gevent", dest="reinit_gevent",
        action="store_true", default=False,
        help="If present, reinitialize gevent in minions after fork." )
    parser.add_option("-m", "--monkey-patch", dest="monkey_patch",
                      action="store_true", default=False,
                      help="If present, also turn on gevent monkey patch.")
    (options,args) = parser.parse_args()

    if len(args) != 1:
        parser.print_help()
        parser.error("Argument must be a comma seperated list of queues")

    log_level = getattr(logging, options.log_level.upper(), 'INFO')
    #logging.basicConfig(level=log_level, format="%(asctime)s: %(levelname)s: %(message)s")

    queues = args[0].split(',')
    server = '%s:%s' % (options.host,options.port)
    Khan.run(pool_size=options.pool_size, queues=queues, server=server,
             logging_level=log_level, log_file=options.logfile,
             blocking_pop=options.blocking_pop,
             reinit_gevent=options.reinit_gevent,
             monkey_patch=options.monkey_patch)


def pyres_scheduler():
    usage = "usage: %prog [options] arg1"
    parser = OptionParser(usage=usage)
    #parser.add_option("-q", dest="queue_list")
    parser.add_option("--host", dest="host", default="localhost")
    parser.add_option("--port",dest="port",type="int", default=6379)
    parser.add_option('-l', '--log-level', dest='log_level', default='info', help='log level.  Valid values are "debug", "info", "warning", "error", "critical", in decreasing order of verbosity. Defaults to "info" if parameter not specified.')
    parser.add_option('-f', dest='logfile', help='If present, a logfile will be used.')
    
    (options,args) = parser.parse_args()
    log_level = getattr(logging, options.log_level.upper(),'INFO')
    #logging.basicConfig(level=log_level, format="%(module)s: %(asctime)s: %(levelname)s: %(message)s")
    setup_logging(log_level=log_level, filename=options.logfile)
    server = '%s:%s' % (options.host, options.port)
    Scheduler.run(server)


def pyres_web():
    usage = "usage: %prog [options]"
    parser = OptionParser(usage)
    parser.add_option("--host",
                    dest="host",
                    default="0.0.0.0",
                    metavar="HOST")
    parser.add_option("--port",
                    dest="port",
                    type="int",
                    default=8080)
    parser.add_option("--dsn",
                      dest="dsn",
                      help="Redis server to display")
    parser.add_option("--server",
                      dest="server",
                      help="Server for itty to run under.",
                      default='wsgiref')
    (options,args) = parser.parse_args()

    server.main(options.host, options.port, options.dsn)


def pyres_worker():
    usage = "usage: %prog [options] arg1"
    parser = OptionParser(usage=usage)

    parser.add_option("--host", dest="host", default="localhost")
    parser.add_option("--port",dest="port",type="int", default=6379)
    parser.add_option("-i", '--interval', dest='interval', default=None, help='the default time interval to sleep between runs')
    parser.add_option('-l', '--log-level', dest='log_level', default='info', help='log level.  Valid values are "debug", "info", "warning", "error", "critical", in decreasing order of verbosity. Defaults to "info" if parameter not specified.')
    parser.add_option('-f', dest='logfile', help='If present, a logfile will be used.')
    parser.add_option("-n", "--nonblocking-pop", dest="blocking_pop", action="store_false", default=True, help="If absent, Pyres will use the Redis blocking pop (BLPOP) to obtain jobs from the queue(s). If present, Redis will use a non-blocking pop (LPOP) and will sleep for up to 8 seconds if no jobs are available.")
    (options,args) = parser.parse_args()

    if len(args) != 1:
        parser.print_help()
        parser.error("Argument must be a comma seperated list of queues")

    log_level = getattr(logging, options.log_level.upper(), 'INFO')
    setup_logging(log_level=log_level, filename=options.logfile)
    interval = options.interval
    if interval is not None:
        interval = int(interval)

    queues = args[0].split(',')
    server = '%s:%s' % (options.host,options.port)
    Worker.run(queues, server, options.blocking_pop, interval)
