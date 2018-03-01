import csv, bpy, os
from math import radians

imgdir = r'C:\Users\aaron\sfm\tranquilitatis\autocrop_wide\\'

for img in bpy.data.images:
    bpy.data.images.remove(img)

cam_data_reader = csv.DictReader(open(r'C:\tmp\cams.csv','r'))
next(cam_data_reader) #skip header row

for line in cam_data_reader:
    print(line['filename'])
    coords = [float(coord) for coord in [line['x'],line['y'],line['z']]]
    SpacecraftAzimuth = float(line['SpacecraftAzimuth'])
    OffNadirAngle = float(line['OffNadirAngle'])
    #bpy.ops.object.camera_add(location=coords, rotation=[0,radians(OffNadirAngle),radians(SpacecraftAzimuth)])
    bpy.ops.object.camera_add(location=coords, rotation=[0,0,0])
    newcam = bpy.context.object
    newcam.name = line['filename']

#    bpy.ops.object.empty_add(location=pit_coords)
#    pit = bpy.context.object
    bpy.ops.object.createcameraimageplane()
    mtlname = 'mat_imageplane_'+line['filename']
    mtl = bpy.data.materials[mtlname]
    imgtxture = mtl.node_tree.nodes['Image Texture']
    imgtxture.image = bpy.data.images.load(filepath=imgdir+line['filename']+'.tif')
    
    look_dir_coords = [float(coord) for coord in [line['look_x'],line['look_y'],line['look_z']]]
    bpy.ops.object.empty_add(location=look_dir_coords)
    look_dir = bpy.context.object
    #look_dir.parent = newcam 
    look_dir.location = look_dir.location + newcam.location #better not to parent because we introduce cyclic dependency
    
    track_to = newcam.constraints.new('TRACK_TO')
    track_to.target = look_dir
    track_to.track_axis = 'TRACK_NEGATIVE_Z'
    track_to.up_axis = 'UP_Y'
    track_to.use_target_z = True
    
    look_dir.rotation_euler[1] = radians(SpacecraftAzimuth)
    newcam.show_name = True