class DH_Cell(object):
	def __init__(self, cell_file): 
		from neuron import h
		h.load_file('stdrun.hoc')
		self.load_cell(cell_file)
		self.x = 0
		self.y = 0
		self.z = 0
		self.all_list = []

	def _xtra_(self):
		for sec in self.all_list:
			sec.insert('xtra')
		from neuron import h
		h.load_file("interpxyz.hoc")    
		h.load_file("setpointers.hoc")  

	def load_cell(self,file_path):
		from neuron import h
		h.load_file(file_path)
		self.cell = h.Cell() ## Create cell
		self.all = h.SectionList() ## Create section list
		self.all.wholetree(sec = self.cell.soma) 



	def set_position(self, x_in, y_in, z_in): 
		from neuron import h
		import math
		h.setpointers()
		midpoint = [self.cell.soma.x_xtra,self.cell.soma.y_xtra,self.cell.soma.z_xtra]
		translation_vector = [x - y for x,y in zip([x_in,y_in,z_in], midpoint)]

		for sec in self.all_list:
			num = int(h.n3d(sec=sec))
			x1 = [0.]*num
			y1 = [0.]*num
			z1 = [0.]*num
			diam = [0.]*num
			for i in range(num):
				x1[i] = h.x3d(i,sec=sec)
				y1[i] = h.y3d(i,sec=sec)
				z1[i] = h.z3d(i,sec=sec)
				diam[i] = h.diam3d(i,sec=sec)
				h.pt3dchange(i,h.x3d(i,sec=sec)+translation_vector[0],h.y3d(i,sec=sec)+translation_vector[1],h.z3d(i,sec=sec)+translation_vector[2],h.diam3d(i,sec=sec),sec=sec)


			