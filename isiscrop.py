#!/usr/bin/env python3

from pysis.isis import camrange, campt, crop, catlab
from pysis.exceptions import ProcessError
import pvl
from clize import run

def crop_latlon(*, center_lat:float, center_lon:float, nsamples, nlines, to_cube, from_cube, pad=None,
                failed_list_to=None):
    print('cropping {}'.format(from_cube))
    try:
        center_campt = pvl.loads(campt(from_= from_cube, type="ground", latitude=center_lat, longitude=center_lon))
        catlab_data = pvl.loads(catlab(from_=from_cube))

    except ProcessError as e:
        print(e.stderr, e.stdout)

    center_pixel = (center_campt['GroundPoint']['Line'], center_campt['GroundPoint']['Sample'])

    #If user asked for max width, start at left edge
    if nsamples == 'max':
        nw_pixel = [center_pixel[0] - int(nlines) / 2, 1]
        nsamples = int(catlab_data['IsisCube']['Core']['Dimensions']['Samples'])
    else:
        nw_pixel = [center_pixel[0] - int(nlines) / 2, center_pixel[1] - int(nsamples) / 2]


    try:
        print("sample:{} line:{}".format(nw_pixel[1], nw_pixel[0]))
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