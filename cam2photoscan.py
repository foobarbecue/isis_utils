#!/usr/bin/env python3

from pysis.isis import campt
from pysis.exceptions import ProcessError
import pvl
from clize import run
from os import path
from glob import glob
import transforms3d
import numpy

ps_cam_xml_template = """<?xml version="1.0" encoding="UTF-8"?>
<document version="1.3.0">
  <chunk>
    <sensors>
        <sensor id="0" label="unknown" type="frame">
        <resolution width="500" height="500"/>
        <property name="fixed" value="0"/>
      </sensor>
    </sensors>
    <cameras>
    {}
    </cameras>
    <reference>
          GEOGCS["GCS_Moon_2000",DATUM["D_Moon_2000",SPHEROID["Moon_2000_IAU_IAG",1737400.0,0.0]], PRIMEM["Reference_Meridian",0.0],UNIT["Degree",0.0174532925199433]]
    </reference>
  </chunk>
</document>
    """

def camera_xml_snippet(id_, ground_point):
    print(id_)
    cam_template = """
    <camera id="{}" label="{}" sensor_id="0" enabled="1">
        <transform>{}</transform>
        <orientation>1</orientation>
        <reference x="{}" y="{}" z="{}" enabled="1"/>
    </camera>
    """
    # Label from filename
    label = path.split(ground_point['Filename'])[-1] + '.tif',

    # Calculate Photoscan-compatible rotation matrix from look direction and body fixed position
    rot_mat = transforms3d.euler.euler2mat(*ground_point['LookDirectionBodyFixed'].value)
    translation_col = numpy.array(ground_point['BodyFixedCoordinate'].value).reshape(3,1)
    bottom_row = numpy.array([0,0,0,1])
    ps_transform = numpy.hstack([rot_mat, translation_col])
    ps_transform = numpy.vstack([ps_transform, bottom_row])
    translation_str = ' '.join([str(x) for x in ps_transform.reshape(1,16).tolist()[0]])

    # Format lat lon alt info for Photoscan reference tag
    lat_lon_alt = [ground_point['SubSpacecraftLongitude'].value,
                   ground_point['SubSpacecraftLatitude'].value,
                   ground_point['SpacecraftAltitude'].value]
    return cam_template.format(id_, label, translation_str, *lat_lon_alt)

def dir2photoscan_cameras(*, from_dir, lat, lon, to_file=None):
    ground_points = []
    for cam_file in glob(from_dir + '*.cub'):
        try:
            ground_point = pvl.loads(
                campt(from_=path.join(from_dir, cam_file), type="ground", latitude=lat, longitude=lon))['GroundPoint']
            #positions.append([cam_file, res['GroundPoint']['SpacecraftPosition']])
            ground_points.append(ground_point)
        except ProcessError as e:
            print(e.stderr)
    cameras = ''.join([camera_xml_snippet(id_, ground_point) for id_, ground_point in enumerate(ground_points)])
    out_xml = ps_cam_xml_template.format(cameras)

    if to_file:
        with open(to_file, 'w') as outfile:
            outfile.write(out_xml)
    else:
        return out_xml

if __name__ == '__main__':
    run(dir2photoscan_cameras)