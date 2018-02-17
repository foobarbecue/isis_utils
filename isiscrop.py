from pysis.isis import camrange, campt, crop
from pysis.exceptions import ProcessError
import pvl

def crop_latlon(center_lat, center_lon, nsamples, nlines, cube_file, pad=None):
    center_campt = pvl.loads(campt(from_= cube_file, type="ground", latitude=center_lat, longitude=center_lon))
    # except ProcessError:
    #     print("Error finding northwest corner. Is it outside the input cube?")

    center_pixel = (center_campt['GroundPoint']['Line'], center_campt['GroundPoint']['Sample'])
    nw_pixel = (center_pixel[0] - nlines / 2, center_pixel[1] - nsamples / 2)

    try:
        crop(from_=cube_file,
             sample=int(nw_pixel[1]),
             line=int(nw_pixel[0]),
             nsamples=nsamples,
             nlines=nlines,
             to="/home/aaron/test.cub")
    except ProcessError as e:
        print(e.stderr, e.stdout)

