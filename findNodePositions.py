def findNodePositions(section,numNewNodes,nodeSpacing):
	from neuron import h
	import math
	section_list = [None]*int(numNewNodes+1)
	
	sec = h.Section()
	parent_section_ref = h.SectionRef(sec = section)
	section_children = parent_section_ref.child
	sec.connect(parent_section_ref.parent(1)) 
	h.disconnect(sec = section)

	arc_Length = 0.0
	points_added = 0

	num_points = h.n3d(sec = sec)
	point1 = 0
	point2 = 1

	while points_added < numNewNodes:
		

		point1_xyz = [h.x3d(point1,sec = section),h.y3d(point1,sec = section),h.z3d(point1,sec = section)]
		point2_xyz = [h.x3d(point2,sec = section),h.y3d(point2,sec = section),h.z3d(point2,sec = section)]
		point_dist = h.arc3d(point2,sec = section) - h.arc3d(point1, sec = section)
		diam1 = h.diam3d(point1,sec=section)
		diam2 = h.diam3d(point2,sec=section)
		h.pt3dadd(h.x3d(point1,sec = section),h.y3d(point1,sec = section),h.z3d(point1,sec = section),h.diam3d(point1,sec=section),sec = sec)
		h.pt3dremove(point1,sec=section)

		if arc_Length + point_dist >= nodeSpacing:
			unit_direction = [x - y for x,y in zip(point2_xyz,point1_xyz)]
			direction_length = [x**2 for x in unit_direction]
			direction_length = math.sqrt(sum(direction_length))
			unit_direction = [x/direction_length for x in unit_direction]
			left_over = (arc_Length + point_dist - nodeSpacing)
			dist_along_line = point_dist - left_over


			new_point = [point1_xyz[0] + dist_along_line*unit_direction[0], point1_xyz[1] + dist_along_line*unit_direction[1], point1_xyz[2] + dist_along_line*unit_direction[2]]
			
			
			diam_point = diam1 + dist_along_line*(diam2-diam1)/point_dist
			arc_Length = 0.0
			h.pt3dinsert(0,new_point[0],new_point[1],new_point[2],diam_point,sec=section)
			h.pt3dadd(new_point[0],new_point[1],new_point[2],diam_point,sec=sec)
			section_list[points_added] = sec
			sec = None
			sec = h.Section()
			points_added += 1
		else:
			arc_Length += point_dist


	section_list[numNewNodes] = section 
	node_list = [None]*(numNewNodes)

	for i in range(numNewNodes):

		node = h.Section()
		node.L = 1
		node.diam = h.diam3d(h.n3d(sec = section_list[i])-1,sec=section_list[i])
		node.connect(section_list[i](1))
		section_list[i+1].connect(node(1))
		node_list[i] = node
		node = None

	h.define_shape()
	return node_list + section_list