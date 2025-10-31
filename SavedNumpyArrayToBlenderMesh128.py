'''
This script should be run in Blender, not GMS
It is the companion script to the GMS python script
Make128x128Surface_ForExport2Blender.py
MWF for UoN October 2025
'''

#Set up the camera 
import mathutils
scn = bpy.context.scene
cam = scn.camera
cam.location = [0.04,5.54,11.2]

def update_camera(camera, focus_point=mathutils.Vector((0.0, 0.0, 0.0)), distance=12.5):
	looking_direction = camera.location - focus_point
	rot_quat = looking_direction.to_track_quat('Z', 'Y')
	camera.rotation_euler = rot_quat.to_euler()
	# Use * instead of @ for Blender <2.8
	camera.location = rot_quat @ mathutils.Vector((0.0, 0.0, distance))

update_camera(bpy.data.objects['Camera'])

# Get data and make 
# Vertices and edges 

import numpy as np
npzfile = np.load('X:/MW Fay/Scripts/Image Processing/BlenderRender/NPArrays128.npz')
x = npzfile['arr_0']
y = npzfile['arr_1']
z = npzfile['arr_2']


# Reshape the three arrays into 1 d list
x = x.reshape(-1)
y = y.reshape(-1)
z = z.reshape(-1)

x = x-64
y = y-64
z = z-min(z)

# Reorient to match dm4 image
z = abs(-z)
x = -x

z_norm = z / (np.linalg.norm(z) + 1e-16)
z_norm = np.multiply(z_norm, 128/(np.max(z_norm)))

# And scale so it isn't giant on display
x = x/32
y = y/32
z_norm = z_norm/(max(z_norm))

#Now combine 
#vertices = np.concatenate((x,y,z_norm), axis=-1)
vertices = np.column_stack((x,y,z_norm))
vertices.astype("float32")

# edges are built when faces are generated
# but it is possible to directly implement edges
# edges = np.array([[0, 1]], dtype=np.int32)
edges = []
#list of edges as pairs of vertex indices

#Need to pair up consecutive ones in rows
#and consecutive ones in columns
for k in range(0,127):
	for l in range (0,127):
		if k<126:
			i = k+l*128
			edges.append((i, i+1))

# and the other orientation
for k in range(0,127):
	for l in range (0,127):
		if l>0:
			i = k+l*128
			edges.append((i, i-128))


faces = [[]]# empty mesh, we'll just create a mesh of edges for now
# Could script in filling at this point, need to match the edges

# build mesh data, object and do some check-up

mesh_data = bpy.data.meshes.new("DM_object_data")
mesh_data.from_pydata(vertices, edges, faces)
mesh_data.update()
mesh_data.validate()      
# This needs to return true, otherwise the following may not work
for f in mesh_data.polygons:
    f.use_smooth = True

obj = bpy.data.objects.new("DM_object", mesh_data)

# add the object to the scene      
scene = bpy.context.scene
scene.collection.objects.link(obj)

# activate the object
obj.select_set(True)
bpy.context.view_layer.objects.active = obj 
bpy.ops.object.mode_set(mode = 'EDIT')
bpy.ops.mesh.select_mode(type="EDGE") 


# Now press F in the UI to make faces
# Also CTRL+V, o to smooth vertices if you haven't median filtered the original data
# Then F12 for render
