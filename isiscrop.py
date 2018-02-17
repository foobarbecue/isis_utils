from pysis.isis import camrange, campt, crop
from pysis.exceptions import ProcessError
import pvl
from numpy import array

import ipdb

def crop_latlon(lat, lon, latrange, lonrange, cube_file):
    # Variables to hold corner locations
    nw = [None]*2
    se = [None]*2

    # Determine the lat / lon extents of the input image cube
    extents = pvl.loads(camrange(from_= cube_file))
    minlat = extents['LatitudeRange']['MinimumLatitude']
    maxlat = extents['LatitudeRange']['MaximumLatitude']
    minlon = extents['UniversalGroundRange']['MinimumLongitude']
    maxlon = extents['UniversalGroundRange']['MaximumLongitude']

    # Calculate corners of desired crop range
    req_minlat = lat - latrange / 2
    req_maxlat = lat + latrange / 2
    req_minlon = lon - lonrange / 2
    req_maxlon = lon + lonrange / 2

    # Limit corners to edge of image range
    if req_maxlat > maxlat:
        nw[0] = maxlat
    else:
        nw[0] = req_maxlat

    if req_minlon < minlon:
        nw[1] = minlon
    else:
        nw[1] = req_minlon

    if req_minlat > minlat:
        se[0] = minlat
    else:
        se[0] = req_minlat

    if req_maxlon < maxlon:
        se[1] = maxlon
    else:
        se[1] = (req_maxlon - 0.05)

    nw_campt = pvl.loads(campt(from_= cube_file, type="ground", latitude=nw[0], longitude=nw[1]))
    se_campt = pvl.loads(campt(from_=cube_file, type="ground", latitude=se[0], longitude=se[1]))
    nw_pixel = array([nw_campt['GroundPoint']['Line'], nw_campt['GroundPoint']['Sample']])
    se_pixel = array([se_campt['GroundPoint']['Line'], se_campt['GroundPoint']['Sample']])
    # ipdb.set_trace()
    extent = se_pixel - nw_pixel
    print("cropping from {} with extent {}".format(nw_pixel, extent))
    try:
        crop(from_=cube_file,
             sample=int(nw_pixel[0]),
             line=int(nw_pixel[0]),
             nsamples=int(extent[0]),
             nlines=int(extent[1]),
             to="/home/aaron/test.cub")
    except ProcessError as e:
        print(e.stderr, e.stdout)

