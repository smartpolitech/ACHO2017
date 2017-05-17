#
# Copyright (C) 2017 by YOUR NAME HERE
#
#    This file is part of RoboComp
#
#    RoboComp is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    RoboComp is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with RoboComp.  If not, see <http://www.gnu.org/licenses/>.
#

import sys, os, Ice, traceback

from time import time,sleep
import configparser
import arrow
from PySide import *
from genericworker import *

ROBOCOMP = ''
try:
	ROBOCOMP = os.environ['ROBOCOMP']
except:
	print '$ROBOCOMP environment variable not set, using the default value /opt/robocomp'
	ROBOCOMP = '/opt/robocomp'
if len(ROBOCOMP)<1:
	print 'genericworker.py: ROBOCOMP environment variable not set! Exiting.'
	sys.exit()


preStr = "-I"+ROBOCOMP+"/interfaces/ --all "+ROBOCOMP+"/interfaces/"
Ice.loadSlice(preStr+"Luces.ice")
from RoboCompLuces import *


from Luces import *
from lifxlan import *
#Consiguiendo luces
num_lights = None
lifx = LifxLAN(verbose=False)
config = configparser.RawConfigParser()
devices = lifx.get_lights()

class SpecificWorker(GenericWorker):
	
	def __init__(self, proxy_map):
		super(SpecificWorker, self).__init__(proxy_map)
		self.timer.timeout.connect(self.compute)
		self.Period = 2000
		self.timer.start(self.Period)
		self.timer.setSingleShot(True);
	def setParams(self, params):
		#try:
		#	par = params["InnerModelPath"]
		#	innermodel_path=par.value
		#	innermodel = InnerModel(innermodel_path)
		#except:
		#	traceback.print_exc()
		#	print "Error reading config params"
		return True

	@QtCore.Slot()
	def compute(self):
		print 'SpecificWorker.compute...'
		num_lights = None
		lifx = LifxLAN(verbose=False)
		config = configparser.RawConfigParser()
		devices = lifx.get_lights()
		print("\n {} luces encontradas \n".format(len(devices)))
		for d in devices:
    			print(d.mac_addr, d.port, d.service, d.source_id, d.ip_addr)
		self.encender()
		sleep(2)
		self.apagar()
		sleep(2)
		self.encender()
		sleep(2)
		self.apagar()
		return True


	#
	# apagar
	#
	def apagar(self):
		print "Apagando luces..."
		for d in devices:
    			d.set_power("off")
    			d.set_power("off")
		


	#
	# encender
	#
	def encender(self):
	 	print "Encendiendo luces..."
		for d in devices:
    			d.set_power("on")
    			d.set_power("on")
		





