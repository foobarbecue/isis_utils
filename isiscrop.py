#!/usr/bin/env python3

from pysis.isis import camrange, campt, crop
from pysis.exceptions import ProcessError
import pvl
from clize import run

def crop_latlon(*, center_lat:float, center_lon:float, nsamples:int, nlines:int, to_cube, from_cube, pad=None,
                failed_list_to=None):
    print('cropping {}'.format(from_cube))
    try:
        center_campt = pvl.loads(campt(from_= from_cube, type="ground", latitude=center_lat, longitude=center_lon))

    except ProcessError as e:
        print(e.stderr, e.stdout)

    center_pixel = (center_campt['GroundPoint']['Line'], center_campt['GroundPoint']['Sample'])
    nw_pixel = (center_pixel[0] - nlines / 2, center_pixel[1] - nsamples / 2)
    try:
        crop(from_=from_cube,
             sample=int(nw_pixel[1]),
             line=int(nw_pixel[0]),
             nsamples=nsamples,
             nlines=nlines,
             to=to_cube)
    except ProcessError as e:
        print(e.stderr, e.stdout)
        if failed_list_to:
            with open(failed_list_to,'a') as failed_list:
                failed_list.write(' {}, {} \n'.format(from_cube, e.stderr))

if __name__ == '__main__':
    run(crop_latlon)