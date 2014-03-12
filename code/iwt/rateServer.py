
# -*- coding: utf-8 -*-

# RateServer

import rater

import pickle
import random

import json

from essay import EssayPassage

import time

import zmq

import threading

import logging

from rater import CollegeEssayRater


class RatePassageThread(threading.Thread):
    def __init__(self, rater, passage):
        threading.Thread.__init__(self)  
        self.rater = rater
        self.passage = passage
        
    def run(self):
        self.rater.rate(passage)

LOG_FILENAME ='rater.log'
logging.basicConfig(filename=LOG_FILENAME,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    level=logging.DEBUG)

if __name__ == "__main__":

    pkfile = open('rater.pkl', 'r')
    rater = pickle.load(pkfile)
    pkfile.close()

    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")
    print "bind ok"
    
    orderId = 1
    waitingPassages = []
    donePassages = {}
    
    passage = None
    while True:
        request = socket.recv()
        print request
        try:
            rs = json.loads(request)
        except:
            socket.send("")
            continue
        if rs['ACTION'] == 'SUBMIT':
            orderId += 1
            newpassage = EssayPassage()
            newpassage.passage = rs['text']
            newpassage.orderId = orderId
            newpassage.score = 0
            newpassage.processStatus = 0
            waitingPassages.append(newpassage)
            if ((not passage) or passage.rated) and len(waitingPassages) > 0:
                passage = waitingPassages.pop(0)
                donePassages[passage.orderId] = passage
                rthread = RatePassageThread(rater, passage)
                rthread.start()
            reply = json.dumps({'orderId':orderId, 'progress':0, 'rated':0})
            socket.send_unicode(reply)
        elif rs['ACTION'] == 'QUERY':
            oId = int(rs['orderId'])
            if not oId in donePassages:
                reply = json.dumps({'orderId':oId, 'progress':0, 'rated':0})
                socket.send_unicode(reply)
            else:
                if passage.rated:
                    reply = json.dumps({'orderId':oId, 'progress':donePassages[oId].processStatus, 
                                    'rated':donePassages[oId].rated, 'resultInfo':donePassages[oId].rateResult})
                else:
                    reply = json.dumps({'orderId':oId, 'progress':donePassages[oId].processStatus, 
                                    'rated':donePassages[oId].rated})
                    print reply
                socket.send_unicode(reply)
            if ((not passage) or passage.rated) and len(waitingPassages) > 0:
                passage = waitingPassages.pop(0)
                donePassages[passage.orderId] = passage
                rthread = RatePassageThread(rater, passage)
                rthread.start()
