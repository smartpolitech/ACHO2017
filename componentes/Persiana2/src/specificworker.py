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
import sys, json, pprint
import datetime 
from subprocess import call, Popen, PIPE
import shlex
import arrow
import time
import sys, os, Ice, traceback, time
from PySide import *
from genericworker import *


ARDUINO = "192.168.0.101"
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
Ice.loadSlice(preStr+"Persiana.ice")
from RoboCompPersiana import *


from persianaI import *

class SpecificWorker(GenericWorker):
	estado = 0
	fecha_ultima_orden = arrow.utcnow() 
	def __init__(self, proxy_map):
		super(SpecificWorker, self).__init__(proxy_map)
		self.timer.timeout.connect(self.compute)
		self.Period = 2000
		
		self.timer.setSingleShot(True);#Para que solo se ejecute 1 vez
		self.timer.start(self.Period)

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
		print ("Estado 1: " + str(SpecificWorker.estado))
		self.recalcularEstado()
		print ("Estado 2: " + str(SpecificWorker.estado))
		return True


	#
	# bajar
	#
	def bajar(self):
		print ("Bajando Persiana...")
		SpecificWorker.fecha_ultima_orden = arrow.utcnow()
		call(["curl", "http://root:opticalflow@" + ARDUINO + "/arduino/command/blinddown"])


	#
	# estadoActual
	#
	def estadoActual(self):
		return SpecificWorker.estado


	#
	# subir
	#
	def subir(self):
		print ("Subiendo Persiana...")
		SpecificWorker.fecha_ultima_orden = arrow.utcnow()
		call(["curl", "http://root:opticalflow@" + ARDUINO + "/arduino/command/blindup"])


	#
	# recalcularEstado
	#
	def recalcularEstado(self):
		curlCommand = "curl -G 'http://10.253.247.18:8086/query?pretty=true' -u guest:smartpolitech --data-urlencode \"db=sensors\" --data-urlencode \"q=select * from UEXCC_INF_P00_DES035_SEN001_ELE where time > now() - 10d\""
		#args = shlex.split(curlCommand)
		process = Popen(shlex.split(curlCommand), stdout=PIPE, stderr=PIPE)
		cadenaMedidas, err = process.communicate()
		medidas = json.loads(str(cadenaMedidas))
		cursor = medidas['results'][0]['series'][0]['values']
		fecha_despues = arrow.get(cursor[-1][0])
		fecha_tot = fecha_despues - SpecificWorker.fecha_ultima_orden 
		#Segundos que ha tardado
		seconds = fecha_tot.seconds 
		print(seconds)
		if seconds > 0 and seconds < 5:
			SpecificWorker.estado = 1
		if seconds >= 5 and seconds <10:
			SpecificWorker.estado = 2 
		if seconds >= 10 and seconds <15:
			SpecificWorker.estado = 3
		if seconds >=15 and seconds <20:
			SpecificWorker.estado = 4
		if seconds >= 20:
			SpecificWorker.estado = 5


	#
	# calibrar
	#
	def calibrar(self):
		#Llamar a la subida
		self.subir()
		#Esperar 30 segundos siempre
		time.sleep(30)
		#Tomar fecha actual
		SpecificWorker.fecha_ultima_orden = arrow.utcnow()
		#llamar a la bajada
		self.bajar()
		time.sleep(30)
		#Guardar el estado
		#Tomar fecha tras bajada
		curlCommand = "curl -G 'http://10.253.247.18:8086/query?pretty=true' -u guest:smartpolitech --data-urlencode \"db=sensors\" --data-urlencode \"q=select * from UEXCC_INF_P00_DES035_SEN001_ELE where time > now() - 10d\""
		#args = shlex.split(curlCommand)
		process = Popen(shlex.split(curlCommand), stdout=PIPE, stderr=PIPE)
		cadenaMedidas, err = process.communicate()
		medidas = json.loads(str(cadenaMedidas))
		cursor = medidas['results'][0]['series'][0]['values']
		#Se obtiene la ultima fecha en la que el motor ha estado activo
		fecha_despues = arrow.get(cursor[-1][0])
		#Calculo de segundos que tarda en bajar
		min_bajada = fecha_despues.datetime.minute - SpecificWorker.fecha_ultima_orden.datetime.minute
		sec_bajada = fecha_despues.datetime.second - SpecificWorker.fecha_ultima_orden.datetime.second
		fecha_tot = fecha_despues - fecha_ultima_orden
		print("Ha tardado " + str(min_bajada) + " minutos y " + str(sec_bajada) + " segundos en bajarse.")
		print(fecha_tot.seconds)
		estado = 0

	#
	# parar
	#
	def parar(self):
		print ("Parando Persiana...")
		call(["curl","http://root:opticalflow@"+ ARDUINO+"/arduino/command/blindstop"])
		self.recalcularEstado()




