import bpy
import csv
import pdb
from numpy import array

bpy.ops.object.select_by_type(type='LAMP')
bpy.ops.object.delete()

sundir_csv_path = r'D:/18-03-03/tranquilitatis/autocrop_wide/cams.csv'
sundir_csv_reader = csv.DictReader(open(sundir_csv_path,'r'))
next(sundir_csv_reader)

for line in sundir_csv_reader:
    caveloc = array([float(line[n]) for n in ('pointing_x','pointing_y','pointing_z')]) 
    sundir = array([float(line[n]) for n in ('SunDir_x','SunDir_y','SunDir_z')])
    sundir = sundir * 50
    bpy.ops.object.lamp_add(type='SUN', location = caveloc + sundir)
    newsun = bpy.context.object
    newsun.name = line['filename']