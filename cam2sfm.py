#!/usr/bin/env python3

from pysis.isis import campt
from pysis.exceptions import ProcessError
import pvl
from clize import run
from os import path
from glob import glob
import transforms3d
import numpy
from math import radians
import pandas

#TODO get resolution numbers from line / samples. PS ignores the cameras if resolution is wrong.
ps_cam_xml_template = """<?xml version="1.0" encoding="UTF-8"?>
<document version="1.3.0">
  <chunk>
    <sensors>
        <sensor id="1" label="unknown" type="frame">
        <resolution width="5064" height="1000"/>
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

xmp_cam_template = """<x:xmpmeta xmlns:x="adobe:ns:meta/">
  <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
      <rdf:Description xcr:Version="2" xcr:PosePrior="locked"
       xmlns:xcr="http://www.capturingreality.com/ns/xcr/1.1#">
      <xcr:Rotation>0 0 {} 0 0 {} 0 0 {}</xcr:Rotation>
      <xcr:Position>{} {} {}</xcr:Position>
    </rdf:Description>
  </rdf:RDF>
</x:xmpmeta>"""

xmp_cam_template_no_rot = """<x:xmpmeta xmlns:x="adobe:ns:meta/">
  <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
      <rdf:Description xcr:Version="2" xcr:PosePrior="locked"
       xmlns:xcr="http://www.capturingreality.com/ns/xcr/1.1#">
      <xcr:Position>{} {} {}</xcr:Position>
    </rdf:Description>
  </rdf:RDF>
</x:xmpmeta>"""

def cam_xml_snippet(id_, ground_point):
    """
    :param id_:
    :param ground_point: PVL output from USGS ISIS campt
    :return: Photoscan-style camera xml file
    """
    cam_template_mat = """<camera id="{}" label="{}" sensor_id="1" enabled="1">
        <orientation>1</orientation>
        <transform>{}</transform>
        <reference x="{}" y="{}" z="{}" enabled="1"/>
    </camera>
    """
    cam_template_xyzypr_ref = """<camera id="{}" label="{}" sensor_id="1" enabled="1">
        <orientation>1</orientation>
       <reference x="{}" y="{}" z="{}" yaw="{}" pitch="{}" roll="{}" enabled="1"/>
    </camera>
    """
    cam_template_ref = """<camera id="{}" label="{}" sensor_id="1" enabled="1">
        <orientation>1</orientation>
        <reference x="{}" y="{}" z="{}" enabled="1"/>
    </camera>
    """
    # Label from filename
    label = path.split(ground_point['Filename'])[-1] + '.tif'
    # Calculate rotation matrix from look direction and body fixed position
    yaw = radians(ground_point['SpacecraftAzimuth'].value)
    roll = radians(ground_point['OffNadirAngle'].value)
    rot_mat = transforms3d.euler.euler2mat(0, yaw, radians(180) + roll, axes='rxzy')

    # Subtract the ground point location from the spacecraft position so we can work in small numbers
    spacecraft_position = numpy.array(ground_point['SpacecraftPosition'].value).reshape(3,1)
    # ground_point_coords = numpy.array(ground_point['BodyFixedCoordinate'].value)
    # translation_col = (spacecraft_position - ground_point_coords).reshape(3,1)
    bottom_row = numpy.array([0,0,0,1])
    ps_transform = numpy.hstack([rot_mat, spacecraft_position])
    ps_transform = numpy.vstack([ps_transform, bottom_row])
    translation_str = ' '.join([str(x) for x in ps_transform.reshape(1,16).tolist()[0]])

    # Format lat lon alt info for Photoscan reference tag
    lat_lon_alt = [ground_point['SubSpacecraftLongitude'].value,
                   ground_point['SubSpacecraftLatitude'].value,
                   ground_point['SpacecraftAltitude'].value * 1000] # cmpt gives alt in km, Photoscan expects m
    yaw_pitch_roll = [0, 0, 0]
    return cam_template_mat.format(id_, label, translation_str, *lat_lon_alt)

def cam_xmp(ground_point):
    """
    :param ground_point: PVL output from USGS ISIS campt
    :return: RealityCapture-style camera xmp file
    """

    # return xmp_cam_template.format(*ground_point['LookDirectionCamera'].value, *ground_point['SpacecraftPosition'].value)
    return xmp_cam_template_no_rot.format(*ground_point['SpacecraftPosition'].value)


def cam_csv(ground_points, to_file):
    """
    :param ground_points: output from ISIS campt
    :return: csv of camera locations
    """
    df = pandas.DataFrame(columns=['filename','x', 'y', 'z'], index='filename')
    for ground_point in ground_points:
        name = ground_point['Filename']
        pos = ground_point['SpacecraftPosition'].value
        df.loc[name, :] = pos
    df.to_csv(to_file)
    return


def dir2sfm_cameras(*, from_dir, lat, lon, out_format=None, to_file=None, return_data=False):
    ground_points = []
    for cam_file in glob(from_dir + '*.cub'):
        print(cam_file)
        cam_file_path = path.join(from_dir, cam_file)
        try:
            ground_point = pvl.loads(
                campt(from_=cam_file_path, type="ground", latitude=lat, longitude=lon))['GroundPoint']
            # positions.append([cam_file, res['GroundPoint']['SpacecraftPosition']])
            ground_points.append(ground_point)
            if out_format == 'xmp':
                with open(cam_file_path + '.xmp', 'w') as xmp_file:
                    xmp_file.write(cam_xmp(ground_point))
        except ProcessError as e:
            print(e.stderr)

    if out_format=='csv':
        cam_csv(ground_points=ground_points, to_file=to_file)

    if out_format=='photoscan':
        cameras = ''.join([cam_xml_snippet(id_, ground_point) for id_, ground_point in enumerate(ground_points)])
        out_xml = ps_cam_xml_template.format(cameras)
        if to_file:
            with open(to_file, 'w') as outfile:
                outfile.write(out_xml)

    if return_data:
        return ground_points

if __name__ == '__main__':
    run(dir2sfm_cameras)