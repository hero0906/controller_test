#coding=utf-8
import httplib
import simplejson
import json
import uuid
import random
import socket
import struct
#import ast
import os
from time import sleep
import paramiko
import log

logger = log.setup()
REST_SERVER = '10.128.121.12'
REST_SERVER_PORT = 7070


class RestException(Exception):
    pass

class RestRequest(object):
    def __init__(self, host=None, port=None):
        self.host = REST_SERVER
        self.port = REST_SERVER_PORT
        self.callbackuri = 'http://%s:%s/debug/result' % (REST_SERVER,
                                                          REST_SERVER_PORT)
        self.headers = self._build_header()

    def _build_header(self):
        headers = {"Content-Type": "application/json",
                   "Accept": "application/json",}

        return headers

    def _send_request(self, uri, method, body, token):
        if not uri:
            raise RestException("uri is required!")

        conn = None
        try:
            conn = httplib.HTTPConnection(self.host, self.port)
            if token:
                self.headers["Cookie"] = token
            conn.request(method, uri, body, self.headers)
            response = conn.getresponse()
            status = response.status
            result = response.read()
        except Exception, e:
            print "Exception: %s" % e
            raise e
        finally:
            if conn:
                conn.close()
        return (status, result)

    def get(self, uri, body=None, token=None):
        return self._send_request(uri, "GET", body, token)

    def post(self, uri, body, token):
        return self._send_request(uri, "POST", body, token)

    def put(self, uri, body, token):
        return self._send_request(uri, "PUT", body, token)

    def delete(self, uri, body, token):
        return self._send_request(uri, "DELETE", body, token)


def bms_callback(req):
    path = '/bms/v1/task/callback'
    body = {
	'taskuuid' : ""
	}
    status, result = req.get(path, None)
    print (status)
    print simplejson.dumps(simplejson.loads(result), indent=4)

def bms_task(req, task_id):
    path = "/bms/v1/task/%s" %(task_id)
    while True:
    	status, result = req.get(path, None)
	results = simplejson.loads(result)
    	task_state = results[u'data'][u'state']
#	logger.debug("image : %s taskid:%s state : %s" %(imageName, task_id, task_state))
	logger.debug(results)
	if str(task_state) == "Completed":
            logger.info(results)
            break
	sleep(5)

def bms_del(req, hostId):
    path = '/bms/v1/delete'
    body = {
    "hostId": hostId,
	}
    data = simplejson.dumps(body)
    try:
    	status, result = req.post(path, data, None)
	results = simplejson.loads(result)
	logger.debug(results)
	return results[u'data'][u'id']
    except Exception,e:
	logger.error(e)
    	return "error"

def bms_power(req, hostId, power):
    path = '/bms/v1/power/%s' %(power)
    body = {"hostId": hostId}
    data = simplejson.dumps(body)
    status, result = req.post(path, data, None)
    #print (status)
    #print simplejson.dumps(simplejson.loads(result), indent=4)
    logger.debug(result)
    logger.info("power %s" %power)
    sleep(2)

def bms_create(req, ImageName):
    path = '/bms/v1/create'
    body = {
	"cpu": 32,
	"hostId": hostId,
	"disks": [
            {
                "capacity": 480,
                "type": "SATA"
            }
	],
	"image": {
	    "imageName": ImageName,
	    "password": password,
	    "username": username
	},
	"monitorIp": "10.240.90.16",
        "nics": [
            {
                "bandwidth": 1000,
                "dns": [
                    "114.114.114.114"
                ],
                "gateway": "114.112.35.25",
                "ipAddress": "114.112.35.26",
                "netmask": "255.255.255.252",
                "vlanId": "1975"
            },
            {
                "bandwidth": 1000,
                "dns": ["114.114.114.114"],
                "ipAddress": "10.240.90.6",
                "vlanId": "1018"
            }
        ],
        "ram": 64
    }
    data = simplejson.dumps(body)
    try:
    	status, result = req.post(path, data, None)
	results = simplejson.loads(result)
	logger.debug(results)
	return results[u'data'][u'id']
    except Exception,e:
	logger.error(e)
    	return "error"

def get_images():
    images = [] 
    lines = os.popen('ls /tftpboot/user_images/|grep 64').read()
    for line in lines.split("\n"):
	images.append(line)
    return images

def ssh2(ip, password):
    try:
	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh.connect(ip, 22, "root", password, timeout=5)
	stdin, stdout, stderr = ssh.exec_command("ip addr")
	out = stdout.readlines()
	logger.info(out)
	ssh.close()
    except Exception,e:
	logger.error(e)


if __name__ == "__main__":
    rest = RestRequest()
    hostIds = ("3")
    #imageNames = get_images()
    loops = 1
    """
    for hostId in hostIds:	
    	bms_power(rest, hostId, "stop")
	#bms_del(rest, hostId)
        task_id = bms_del(rest, hostId)
        logger.info("bms delete task starting")
        if task_id != "error":
            bms_task(rest, task_id)
            logger.info("bms delete task successful")
        else:
            logger.error("Image:, del task fail!!!")
    """
    for hostId in hostIds:
        imageName = "rhel7.6_64"
        username, password = ("root", "bms@@@001")
	bms_power(rest, hostId, "stop")
        task_id = bms_create(rest, imageName)
        bms_task(rest, task_id)



"""
    while True:
	logger.info("testing loops %s >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>" %loops)
        for imageName in imageNames: 
            if imageName[:3] == "win":
    		username, password = ("administrator", "bms@@@001")
            else:
    		username, password = ("root", "bms@@@001")
    	    logger.info("bms create task %s starting" %imageName)
            task_id = bms_create(rest, imageName)
            if task_id != "error":
    		bms_task(rest, task_id)
    		logger.info("bms create task %s successful" %imageName)
    	        ping_status = os.system("ping 114.112.35.18 -c 3")
		if ping_status: 
    			logger.error("ip 114.112.35.18 configure fail")
    	    	else:
    			logger.debug("ip 114.112.35.18 configure success")
    	    		if username == "root":
    				logger.info("ssh login %s %s %s" %(imageName, username, password))
    				ssh2("114.112.35.18", password)
            else:
    		logger.error("Image:%s, create task fail!!!" %(imageName))
    
            bms_power(rest, hostId, "stop")

    	    task_id = bms_del(rest, hostId)
    	    logger.info("bms delete task %s starting" %imageName)
            if task_id != "error":
                bms_task(rest, task_id)
    		logger.info("bms delete task %s successful" %imageName)
            else:
    		logger.error("Image:%s, del task fail!!!" %(imageName))
    
            bms_power(rest, hostId, "stop")
	    loops +=1

"""
