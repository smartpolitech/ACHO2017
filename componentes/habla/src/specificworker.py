# -*- coding: utf-8 -*-
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

import sys, os, traceback, time

from PySide import *
from genericworker import *

#lib for habla
import time #execution
from textblob import TextBlob #translation
import textblob #exception
from practnlptools.tools import Annotator #srl
import re #split delim
from difflib import SequenceMatcher #percent equal sentence

#class result
class Result:
        def __init__(self, success, reason, result):
                self.success = success
                self.reason = reason
                self.result = result

# If RoboComp was compiled with Python bindings you can use InnerModel in Python
# sys.path.append('/opt/robocomp/lib')
# import librobocomp_qmat
# import librobocomp_osgviewer
# import librobocomp_innermodel

class SpecificWorker(GenericWorker):
	def __init__(self, proxy_map):
		super(SpecificWorker, self).__init__(proxy_map)
		self.timer.timeout.connect(self.compute)
		self.Period = 2000
		self.timer.start(self.Period)

	def setParams(self, params):
		#try:
		#	self.innermodel = InnerModel(params["InnerModelPath"])
		#except:
		#	traceback.print_exc()
		#	print "Error reading config params"
		return True

	@QtCore.Slot()
	def compute(self):
		print 'SpecificWorker.compute...'
		#computeCODE
		#try:
		#	self.differentialrobot_proxy.setSpeedBase(100, 0)
		#except Ice.Exception, e:
		#	traceback.print_exc()
		#	print e

		# The API of python-innermodel is not exactly the same as the C++ version
		# self.innermodel.updateTransformValues("head_rot_tilt_pose", 0, 0, 0, 1.3, 0, 0)
		# z = librobocomp_qmat.QVec(3,0)
		# r = self.innermodel.transform("rgbd", z, "laser")
		# r.printvector("d")
		# print r[0], r[1], r[2]

		return True

	#read dictionary
	def readDic(self):
        	dicc = open('~/habla/files/dicc.txt', 'r')
	        dicc_2 = dicc.read().split('\n')
        	dicc.close()
	        return dicc_2

	#translate de command
	def traduccion(self, message):
        	message = message
	        sen_orig = TextBlob(message)
        	lan_orig = sen_orig.detect_language()
	        lan_dest = 'en'
        	success = False
	        reason = " "
        	result = " "
	        try:
        	        result = str(sen_orig.translate(to=lan_dest))
                	success = True
	        except textblob.exceptions.TextBlobError:
        	        reason = "No he entendido. Repite.\n"
	        r = Result(success, reason, result)
        	return r

	#semantic role labeling
	def srl(self, sen_dest):
        	ant = Annotator()
	        if sen_dest.upper().split()[0] == "UP":
        	        v = sen_dest.upper().split()
                	v[0] = "RAISE"
	                sen_dest = str(v)
        	sen_srl =  ant.getAnnotations(sen_dest)['syntax_tree']
        	return sen_srl

	#get verb and noun
	def verb_noun(self, sen_srl):
        	success = False
	        reason = " "
        	result = " "
	        verb = ""
        	noun = ""
	        o = sen_srl.split(')')[0]
        	n = re.split(r'[()]+', sen_srl)
	        if (('RB' in o) or ('VB' in sen_srl)) and (('NN' in sen_srl)):
        	        if 'RB' in o:
	                        verb = o.split()[1]
                	for e in n:
                        	if ('VB' in e) and ('RB' not in o):
                                	verb = e.split()[1]
	                        if (('IN' in e) or ('RP' in e)) and ((verb != 'is') or (verb != 'or')) and verb != "":
        	                        verb = verb + e.split()[1]
                	        if 'NN' in e:
                        	        noun = e.split()[1]
	                success = True
        	else:
                	reason =  "\nEl comando debe tener verbo y sustantivo. REPITA."
	        result = verb + " " + noun
        	r = Result(success, reason, result)
	        return r

	#match verb and noun by %
	def match(self, sen):
        	verb = sen.split()[0]
	        noun = sen.split()[1]
        	dicc_2 = self.readDic()
	        nverb_max = 0
        	verb_max = ""
	        nnoun_max = 0
        	noun_max = ""
	        for i in dicc_2[:-1]:
        	        m = SequenceMatcher(None, i.split(':')[0], verb.upper()).ratio()
                	if m > nverb_max:
                        	nverb_max = m
	                        verb_max = i.split(':')[0]
        	                sverb_max = i.split(':')[1].split(',')
	        for i in sverb_max:
        	        m = SequenceMatcher(None, noun.upper(), i).ratio()
                	if m > nnoun_max:
                        	nnoun_max = m
	                        noun_max = i
        	return verb_max + " " + noun_max, str(nverb_max), str(nnoun_max)

	#result
	def result(self, command, data):
        	phrase = data[0]
	        nverb_max = float(data[1])
        	nnoun_max = float(data[2])
	        success = False
        	reason = " "
	        if nverb_max >= 0.8:
        	        if nnoun_max >= 0.8:
                	        reason =  "\nDo action: " + phrase
                        	success = True
	                elif nnoun_max >= 0.6:
        	                reason =  ("\nQuisa dijo: " + phrase + " ")
                	else:
                        	reason =  "\nNo se ha encontrado el comando: " + command + ". Por favor, diga un comando valido."
	        elif (nverb_max >= 0.6) and (nverb_max < 0.8) and (nnoun_max >= 0.6):
        	        reason = ("\nQuisa dijo: " + phrase + " ")
	        else:
        	        reason =  "\nNo se ha encontrado el comando: " + command + ". Por favor, diga un comando valido."
	        r = Result(success, reason, " ")
        	return r

        #
        # procesa
        #
	def procesa(self, message):
		#
		#implementCODE
		#
		res = Res()
		res_trad = self.traduccion(message)
		if res_trad.success == False:
			res.success = res_trad.success
			res.reason = res_trad.reason
		else:
			sen_srl = self.srl(res_trad.result)
			res_vn = self.verb_noun(sen_srl)
			if res_vn.success == False:
				res.success = res_vn.success
				res.reason = res_vn.reason
			else:
				data = self.match(res_vn.result)
				res_res = self.result(message, data)
				res.success = res_res.success
				res.reason = res_res.reason
		print res.reason
		print res.success
		return res



