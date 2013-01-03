Pyres - a Resque clone (Pinterest fork)
=======================================

## Changes in the Pinterest fork

We've added some features to the upstream Pyres codebase that should be useful for a wide range of Pyres users. Here's some information about what we added:

### Better support for multiple queues

Standard Pyres performs a `BLPOP` (blocking pop) operation to obtain jobs from Redis. The blocking pop operation pulls a job from the queue, but if the queue is empty, it waits up to 10 seconds for a new job.

The blocking pop operation allows for a very clever implementation, but it doesn't work well when Pyres is pulling jobs from more than one queue. At Pinterest we use 10 queues so that we can prioritize different tasks. We process all jobs in the p10 queue before moving on to p9, p8, etc. Because Pyres uses `BLPOP`, this won't work correctly. Pyres will wait 10 seconds on p10, then wait 10 seconds on p9, and so on. A worker would take 100 seconds to get through our 10 queues before checking p10 again.

Our fork adds an option to use `LPOP` instead, which is a non-blocking pop operation. Redis will return a task if there's one available, but it won't wait for a new task to be added to the queue. Your pyres_worker will poll every queue as soon as it finishes a task. If all the queues are empty, it will pause for 1 second, and then poll all the queues again. If there still aren't any jobs in the queues, it will back off and poll slower, eventually pausing up to 8 seconds before polling the queues.

To enable `LPOP`, add `--nonblocking-pop` to the command line.

### Support for gevent-backed libraries

At Pinterest we have some worker tasks that require the gevent network library. Gevent needs to be re-initialized in each worker thread after that thread has been forked from the pyres_manager. To enable gevent re-initialization in the workers, add `--reinit-gevent` to the command line.

### Aggregate multiple Redis servers in Pyres Web interface

Our fork lets you aggregate tasks from multiple Redis servers in the web UI (pyres_web). If you have spread your queues across more than one Redis server, you can pass a comma-delimited list of DSNs in the `--dsn` command line parameter.

### Better graceful shutdown support

When the pyres_master is asked to shut down -- when it receives the SIGTERM signal -- it forwards the SIGTERM to all of its child pyres_worker processes. This asks the child processes to shut down as well, but it doesn't *force* the children to shut down. A misbehaving child can ignore the SIGTERM, which will prevent the master from ever shutting down. Our fork waits up to 10 seconds for its children to finish their current tasks, and then forcibly kills those processes.

Note that this may cause you to lose some tasks -- they won't be placed back into their queue, or even into the failed queue.


## About Pyres

[Resque](http://github.com/defunkt/resque) is a great implementation of a job queue by the people at github. It's written in ruby, which is great, but I primarily work in python. So I took on the task of porting over the code to python and PyRes was the result


## Project Goals

Because of some differences between ruby and python, there are a couple of places where I chose speed over correctness. The goal will be to eventually take the application and make it more pythonic without sacrificing the awesome functionality found in resque. At the same time, I hope to stay within the bounds of the original api and web interface.


## Running Tests

 1. Install nose: `$ easy_install nose`
 2. Start redis: `$ redis-server [PATH_TO_YOUR_REDIS_CONFIG]`
 3. Run nose: `$ nosetests` Or more verbosely: `$ nosetests -v`


##Mailing List

To join the list simply send an email to <pyres@librelist.com>. This
will subscribe you and send you information about your subscription,
include unsubscribe information.

The archive can be found at <http://librelist.com/browser/>.


## Information

* Code: `git clone git://github.com/binarydud/pyres.git`
* Home: <http://github.com/binarydud/pyres>
* Docs: <http://binarydud.github.com/pyres/>
* Bugs: <http://github.com/binarydud/pyres/issues>
* List: <pyres@librelist.com>

## TODO

Stabalize the api.

Add a pre-fork worker module