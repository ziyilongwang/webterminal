#!/usr/bin/env python
#coding:utf-8
from flask import Flask, render_template
from flask_sockets import Sockets
from utility.myDocker import ClientHandler, DockerStreamThread
import conf
from thread_send import threadSend

app = Flask(__name__)
sockets = Sockets(app)

@app.route('/')
def index():
    return render_template('index.html')

@sockets.route('/echo')
def echo_socket(ws):
    dockerCli = ClientHandler(base_url=conf.DOCKER_HOST, timeout=10)
    terminalExecId = dockerCli.creatTerminalExec(conf.CONTAINER_ID)
    print terminalExecId
    #terminalStream = dockerCli.startTerminalExec(terminalExecId)
    terminalStream = dockerCli.startTerminalExec(terminalExecId)
    terminalStream.settimeout(600)
    send = threadSend(ws,terminalStream)
    send.start()
    while not ws.closed:
        message = ws.receive()
        if message is not None:
            terminalStream.send(message)
   
if __name__ == '__main__':
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
    server.serve_forever()
