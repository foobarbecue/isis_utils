from pysis.isis import campt, crop
from pysis.exceptions import ProcessError
import pvl
from numpy import array

import ipdb

def crop_latlon(lat, lon, latrange, lonrange, cube_file):
    nw = (lat + latrange / 2, lon - lonrange / 2)
    se = (lat - latrange / 2, lon + lonrange / 2)
    nw_campt = pvl.loads(campt(from_= cube_file, type="ground", latitude=nw[0], longitude=nw[1]))
    se_campt = pvl.loads(campt(from_=cube_file, type="ground", latitude=se[0], longitude=se[1]))
    nw_pixel = array([nw_campt['GroundPoint']['Line'], nw_campt['GroundPoint']['Sample']])
    se_pixel = array([se_campt['GroundPoint']['Line'], se_campt['GroundPoint']['Sample']])
    # ipdb.set_trace()
    extent = se_pixel - nw_pixel
    try:
        crop(from_=cube_file,
             sample=int(nw_pixel[0]),
             line=int(nw_pixel[0]),
             nsamples=int(extent[0]),
             nlines=int(extent[1]),
             to="/home/aaron/test.cub")
    except ProcessError as e:
        print(e.stderr, e.stdout)

