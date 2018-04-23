import os
import pytest

from jwst.helpers import get_bigdata, require_bigdata, cmp_fitshdr
from shutil import copyfile
from astropy.io import fits
from jwst.lib.set_telescope_pointing import add_wcs


@require_bigdata
def test_miri_setpointing():
    """
    Regression test of the set_telescope_pointing script on a level-1b MIRI file.
    """

    try:
        os.remove(_bigdata+'/miri/test_pointing/jw80600010001_02101_00001_mirimage_uncal.fits')
    except:
        pass

    # Copy original version of file to test file, which will get overwritten by test
    copyfile(_bigdata+'/miri/test_pointing/jw80600010001_02101_00001_mirimage_uncal_orig.fits',
             _bigdata+'/miri/test_pointing/jw80600010001_02101_00001_mirimage_uncal.fits')

    add_wcs(_bigdata+'/miri/test_pointing/jw80600010001_02101_00001_mirimage_uncal.fits')

    h = fits.open(_bigdata+'/miri/test_pointing/jw80600010001_02101_00001_mirimage_uncal.fits')
    href = fits.open(_bigdata+'/miri/test_pointing/jw80600010001_02101_00001_mirimage_uncal_ref.fits')
    newh = fits.HDUList([h['primary'],h['sci'],h['refout'],h['group']])
    newhref = fits.HDUList([href['primary'],href['sci'],href['refout'],href['group']])
    result = fits.diff.FITSDiff(newh, newhref,
                              ignore_keywords = ['DATE','CAL_VER','CAL_VCS','CRDS_VER','CRDS_CTX'],
                              rtol = 0.000001)
    assert result.identical, result.report()
