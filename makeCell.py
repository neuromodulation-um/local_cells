from neuron import h,gui
import numpy as np
import random
import math
from findNodePositions import *
import sys
from DH_Cell import *
h.load_file('stdrun.hoc')

if len(sys.argv) > 0:
	nrn = int(sys.argv[1])
else:
	nrn = 1 ## Base model -- Fastest simulation and most strongly polarized

if nrn == 1:
	a = DH_Cell('int1.hoc')
	name = 'int1'
if nrn == 2:
	a = DH_Cell('int2.hoc')
	name = 'int2'
if nrn == 3:
	a = DH_Cell('int3.hoc')
	name = 'int3'
if nrn == 4:
	a = DH_Cell('pn1.hoc')
	name = 'pn1'
if nrn == 5:
	a = DH_Cell('pn2.hoc')
	name = 'pn2'


old_axon_list = h.SectionList()
new_axon_list = h.SectionList()
nodes = h.SectionList()
old_axon_list = a.cell.axon
children = h.SectionList()
new_axon_index = 0
node_list = []
new_axon_list = []
#### ADD nodes at branches

for sec in old_axon_list:
	sec_ref = h.SectionRef(sec=sec)
	num_children = len(sec_ref.child)
	if num_children > 1:
		node = h.Section()
		node.diam = h.diam3d(h.n3d(sec=sec)-1,sec=sec)
		child_sec_list = list(sec_ref.child)
		pt1 = [h.x3d(int(h.n3d(sec=sec)-2),sec = sec),h.y3d(int(h.n3d(sec=sec)-2),sec = sec),h.z3d(int(h.n3d(sec=sec)-2),sec = sec)]
		pt2 = [h.x3d(int(h.n3d(sec=sec)-1),sec = sec),h.y3d(int(h.n3d(sec=sec)-1),sec = sec),h.z3d(int(h.n3d(sec=sec)-1),sec = sec)]
		direction_L = math.sqrt(sum([(y-x)**2 for (y,x) in zip(pt2,pt1)]))
		direction = [(y-x)/direction_L for (y,x) in zip(pt2,pt1)] 
		h.pt3dadd(h.x3d(int(h.n3d(sec=sec)-1),sec = sec),h.y3d(int(h.n3d(sec=sec)-1),sec = sec),h.z3d(int(h.n3d(sec=sec)-1),sec = sec),h.diam3d(int(h.n3d(sec=sec)-1),sec=sec),sec = node)
		h.pt3dadd(h.x3d(int(h.n3d(sec=sec)-1),sec = sec) + direction[0], h.y3d(int(h.n3d(sec=sec)-1),sec = sec) + direction[1],h.z3d(int(h.n3d(sec=sec)-1),sec = sec) + direction[2], h.diam3d(int(h.n3d(sec=sec)-1),sec=sec), sec = node)
		for child_sec in child_sec_list:
			h.disconnect(sec=child_sec)
			child_sec.connect(node(1))
		node.connect(sec(1))
		node_list.append(node)
		sec_ref = None
		node = None
#
h.define_shape()
axon_with_nodes_list = h.SectionList()
axon_with_nodes_list.subtree(sec=old_axon_list[0])

###################################

for sec in old_axon_list:
	numPointsSection = h.n3d(sec=sec)
	mid_diam = sec(0.5).diam
	nodeSpacing = mid_diam*100.0 ## Spacing between nodes
	numNewNodes = (sec.L - 1.5*nodeSpacing)/(nodeSpacing - .0000001)
	if numNewNodes >= 0:
		numNewNodes = int(numNewNodes) + 1
	else:
		numNewNodes = 0

	if numNewNodes > 0 and sec(0.5).diam > .2:
		new_sections = findNodePositions(sec,numNewNodes,nodeSpacing)
		index = 0
		for new_sec in new_sections:
			if index >= numNewNodes:
				new_axon_list.append(new_sec)
				new_sec.cm = 1000
			else:
				node_list.append(new_sec)
			index += 1
	else:
		if sec(0.5).diam > 0.2:
			sec.cm = 1000
		new_axon_list.append(sec)


#### Add nodes to end
for sec in new_axon_list:
	sec_ref = h.SectionRef(sec = sec)
	num_children = len(sec_ref.child)
	if num_children == 0:	## All terminals
		pt1 = [h.x3d(0,sec = sec),h.y3d(0,sec = sec),h.z3d(0,sec = sec)]
		pt2 = [h.x3d(int(h.n3d(sec=sec)-1),sec = sec),h.y3d(int(h.n3d(sec=sec)-1),sec = sec),h.z3d(int(h.n3d(sec=sec)-1),sec = sec)]
		direction_L = math.sqrt(sum([(y-x)**2 for (y,x) in zip(pt2,pt1)]))
		direction = [(y-x)/direction_L for (y,x) in zip(pt2,pt1)] 

		newNode = h.Section()
		newNode.diam = sec(1).diam
		newNode.cm = .85
		newNode.connect(sec,1)
		node_list.append(newNode)
		h.pt3dclear(sec = newNode)
		h.pt3dadd(h.x3d(int(h.n3d(sec=sec)-1),sec = sec),h.y3d(int(h.n3d(sec=sec)-1),sec = sec),h.z3d(int(h.n3d(sec=sec)-1),sec = sec),h.diam3d(int(h.n3d(sec=sec)-1),sec=sec),sec = newNode)
		h.pt3dadd(h.x3d(int(h.n3d(sec=sec)-1),sec = sec) + direction[0], h.y3d(int(h.n3d(sec=sec)-1),sec = sec) + direction[1],h.z3d(int(h.n3d(sec=sec)-1),sec = sec) + direction[2], h.diam3d(int(h.n3d(sec=sec)-1),sec=sec), sec = newNode)
	sec_ref = None

		
all_list = list(node_list) + list(new_axon_list) + list([a.cell.soma]) + list(a.cell.dend) + list([a.cell.ais])	
a.all_list = all_list
a.node_list = node_list

h.define_shape()


for sec in a.all_list:
	h.pt3dstyle(0,sec = sec)
	h.pt3dconst(1.0, sec = sec)



node_sodium = 1.8
node_potassium = .3

k_reversal = -84
na_reversal = 60
R2 = 200
base_capacitance = .85
g_pas = .000018


for sec in all_list:

	sec.insert('pas')
	sec.insert('extracellular')
	sec.e_pas = -70.
	sec.g_pas = g_pas #(1.1e-5)
	#sec.cm = 1
	sec.Ra = R2
	sec.insert('B_Na')
	sec.insert('KDRI_Shifted')
	sec.gnabar_B_Na = 0
	sec.gkbar_KDRI_Shifted   = 0
	sec.ek = k_reversal
	sec.ena = na_reversal

for sec in node_list:
	sec.gnabar_B_Na = node_sodium 
	sec.gkbar_KDRI_Shifted  = node_potassium
	sec.ek = k_reversal
	sec.Ra = R2
	sec.cm = base_capacitance


for sec in new_axon_list:
	num = int(h.n3d(sec=sec))
	sec.Ra = R2
	if sec.cm > 10:
		# If myelinated
		for i in range(num):
	 		h.pt3dchange(i,h.diam3d(i,sec = sec)*1.25 ,sec=sec) ## Adjust different values
		sec.g_pas = 1.125e-6
		sec.cm = .02
		sec.nseg = 11 ## Good starting point, but should be checked to make sure this is enough segments
	else:
		# If unmyelinated
		sec.g_pas = g_pas 
		sec.diam = sec.diam
		sec.cm = base_capacitance
		sec.gnabar_B_Na = 0.6 
		sec.gkbar_KDRI_Shifted  =  .076
		sec.nseg = 9


for sec in all_list:
	if sec.cm > .2:
		sec.cm = base_capacitance


a.cell.soma.gnabar_B_Na = .008 ## Original
a.cell.soma.gkbar_KDRI_Shifted  = .0043 ## Original
a.cell.soma.ek = k_reversal
a.cell.soma.nseg = 11


for sec in a.cell.dend:
	sec.gkbar_KDRI_Shifted = 0.1
	sec.insert('B_Na')
	sec.gnabar_B_Na = .008


for sec in a.all_list:
	if sec.L > 25:
		sec.nseg = int(sec.L/3)
		if sec.nseg % 2 == 0:
			sec.nseg = sec.nseg + 1 

a.cell.ais.gnabar_B_Na = node_sodium
a.cell.ais.gkbar_KDRI_Shifted = node_potassium
a.cell.ais.ek = k_reversal
a.cell.ais.nseg = 21
a.cell.ais.Ra = R2


h.psection(sec = a.cell.soma)
a._xtra_()
a.set_position(0,0,0)

h.define_shape()
h.setpointers()




####### Delete terminal nodes on unmyelinated branches #######
updated_node_list = []
updated_axon_list = []

nodes_to_delete = []
sl = h.allsec()

for sec in node_list:
	sref = h.SectionRef(sec = sec)
	par = sref.parent
	# print par.L
	nchild = sref.nchild()
	if nchild == 0 and par.cm == base_capacitance:
		par_ref = h.SectionRef(sec = par)
		parx2 = par_ref.parent
		nodes_to_delete.append(sec)
		sec = None
	else:
		updated_node_list.append(sec)





all_list = None
a.all_list = None
node_list = None
a.node_list = None
sl = None
nodes_to_delete = None
sec = None
sec2 = None

sl = h.allsec()



axon_to_delete = []
for sec in new_axon_list:
	if sec.cm < 0.5:
		updated_axon_list.append(sec)
		continue
	sref = h.SectionRef(sec = sec)
	nchild = sref.nchild()
	par    = sref.parent
	if nchild == 0 and par.L < 1.02 and par.L > 0.98 and sec.L < 50:
		h.delete_section(sec=sec)
		axon_to_delete.append(sec)
		sec = None
	else:
		updated_axon_list.append(sec)


axon_to_delete = None
axon_with_nodes_list = None
old_axon_list = None
new_sections = None
node_list = updated_node_list
new_axon_list = updated_axon_list
a.node_list = updated_node_list
a.all_list = list(updated_node_list) + list(updated_axon_list) + list([a.cell.soma]) + list(a.cell.dend) + list([a.cell.ais])	


for sec in a.node_list:
	sref = h.SectionRef(sec = sec)
	par = sref.parent
	if par.cm == .85:
		sec.gnabar_B_Na = 0.6 
		sec.gkbar_KDRI_Shifted  = .076
##################################################################




for sec in a.all_list:
	h.pt3dstyle(0,sec = sec)
	h.pt3dconst(0, sec = sec)
for sec in new_axon_list:
	if sec.cm < .05:
		sref = h.SectionRef(sec = sec)
		child_sec = sref.child[0]
		sref2 = h.SectionRef(sec = child_sec)
		numchild = sref2.nchild()
		if numchild == 0:
			if sec.L/sec.diam < 70:

				needed_ratio = 70 - sec.L/sec.diam
				needed_dist = sec.diam * needed_ratio

				numpPtsInSection = int(h.n3d(sec = sec))
				direction = [h.x3d(numpPtsInSection -1, sec = sec) - h.x3d(numpPtsInSection - 2,sec = sec),h.y3d(numpPtsInSection -1, sec = sec) - h.y3d(numpPtsInSection - 2,sec = sec),h.z3d(numpPtsInSection -1, sec = sec) - h.z3d(numpPtsInSection - 2,sec = sec)]
				direction_magnitude = (direction[0]**2 + direction[1]**2 + direction[2]**2)**0.5

				direction = [pt/direction_magnitude for pt in direction]


				numNewPts = int(math.ceil(needed_dist/5.0))
				starting_point = [h.x3d(numpPtsInSection-1, sec = sec), h.y3d(numpPtsInSection-1, sec = sec), h.z3d(numpPtsInSection-1, sec = sec)]
				newDiam = h.diam3d(numpPtsInSection - 1 ,sec = sec)
				for i in range(numNewPts):
					ptNumber = i + 1
					h.pt3dadd(starting_point[0] + (ptNumber*5.0)*direction[0], starting_point[1] + (ptNumber*5.0)*direction[1], starting_point[2] + (ptNumber*5.0)*direction[2], newDiam, sec = sec)
				sec.nseg = 7

h.setpointers()
h.define_shape()
h.setpointers()


while 1 == 1:
	pass