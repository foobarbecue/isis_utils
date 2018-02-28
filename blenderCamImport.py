import csv, bpy
from math import radians

cam_data_reader = csv.DictReader(open(r'C:\tmp\cams.csv', 'r'))
next(cam_data_reader)  # skip header row
for line in cam_data_reader:
    print(line['filename'])
    coords = [float(coord) for coord in [line['x'], line['y'], line['z']]]
    SpacecraftAzimuth = float(line['SpacecraftAzimuth'])
    bpy.ops.object.camera_add(location=coords, rotation=[0, 0, radians(SpacecraftAzimuth)])
    bpy.context.object.name = line['filename']
    bpy.ops.object.createcameraimageplane()
    mtlname = 'mat_imageplane_' + line['filename']
    mtl = bpy.data.materials[mtlname]
    imgtxture = mtl.node_tree.nodes['Image Texture']
    imgtxture.image = bpy.data.images.load(
        filepath='C:\\Users\\aaron\\sfm\\tranquilitatis\\autocrop_wide\\' + line['filename'] + '.tif')
