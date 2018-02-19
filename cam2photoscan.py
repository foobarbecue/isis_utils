#!/usr/bin/env python3

from pysis.isis import campt
from pysis.exceptions import ProcessError
import pvl
from clize import run
from os import path
from glob import glob

ps_cam_xml_template = """
<?xml version="1.0" encoding="UTF-8"?>
<document version="1.3.0">
  <chunk>
    <sensors>
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

def camera_xml_snippet(position):
    cam_template = """
    <camera id="2" label="{}" sensor_id="0" enabled="1">
        <orientation>1</orientation>
        <reference x="{}" y="{}" z="{}" enabled="1"/>
    </camera>
    """
    return cam_template.format(*position)

def dir2photoscan_cameras(*, from_dir, lat, lon, to_file):
    positions = []
    for cam_file in glob(from_dir + '*.cub'):
        try:
            res = pvl.loads(campt(from_=path.join(from_dir, cam_file), type="ground", latitude=lat, longitude=lon))
            #positions.append([cam_file, res['GroundPoint']['SpacecraftPosition']])
            positions.append([cam_file,
                              res['GroundPoint']['SubSpacecraftLongitude'][0],
                              res['GroundPoint']['SubSpacecraftLatitude'][0],
                              res['GroundPoint']['SpacecraftAltitude'][0]
                              ])
        except ProcessError as e:
            print(e.stderr)

    out_xml = ps_cam_xml_template.format(''.join([camera_xml_snippet(cam) for cam in positions]))
    with open(to_file, 'w') as outfile:
        outfile.write(out_xml)

if __name__ == '__main__':
    run(dir2photoscan_cameras)