#!/usr/bin/env python3

from pysis.isis import campt
from pysis.exceptions import ProcessError
import pvl
from clize import run
from os import path
from glob import glob

def dir2photoscan_cameras(*, from_dir, lat, lon):
    positions = []
    for cam_file in glob(from_dir + '*.cub'):
        try:
            res = pvl.loads(campt(from_=path.join(from_dir, cam_file), type="ground", latitude=lat, longitude=lon))
            positions.append([cam_file, res['GroundPoint']['SpacecraftPosition']])
        except ProcessError as e:
            print(e.stderr)

    return positions

def camera_xml_snippet(cam_file, position):
    cam_template = """
        <camera id="2" label="{}" sensor_id="0" enabled="1">
        <transform>9.9911281627221693e-001 -3.1746238076266690e-002 -2.7672309780788919e-002 -8.3246669889896943e+000 -3.2885473393427074e-002 -9.9858736724610764e-001 -4.1735064588156137e-002 5.4560125134044235e-001 -2.6308287673072750e-002 4.2608054925006369e-002 -9.9874542685071577e-001 -1.4738047749381413e+000 0.0000000000000000e+000 0.0000000000000000e+000 0.0000000000000000e+000 1.0000000000000000e+000</transform>
        <orientation>1</orientation>
        <reference x="{x}" y="{x}" z="{z}" enabled="1"/>
      </camera>
    """
    return cam_template.format(file, *position)


    ps_cam_xml_template = """
<?xml version="1.0" encoding="UTF-8"?>
<document version="1.3.0">
  <chunk>
    <sensors>
    </sensors>
    <cameras>
    </cameras>
  </chunk>
</document>
    """


