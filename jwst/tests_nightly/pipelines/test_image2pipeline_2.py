import os
import pytest
from astropy.io import fits
from jwst.pipeline.calwebb_image2 import Image2Pipeline

pytestmark = [
    pytest.mark.usefixtures('_jail'),
    pytest.mark.skipif(not pytest.config.getoption('bigdata'),
                       reason='requires --bigdata')
]

def test_image2pipeline2(_bigdata):
    """

    Regression test of calwebb_image2 pipeline performed on NIRCam data.

    """

    Image2Pipeline.call(_bigdata+'/pipelines/jw82500001003_02101_00001_NRCALONG_rate_ref.fits',
                        output_file='jw82500001003_02101_00001_NRCALONG_cal.fits')

    h = fits.open('jw82500001003_02101_00001_NRCALONG_cal.fits')
    href = fits.open(_bigdata+'/pipelines/jw82500001003_02101_00001_NRCALONG_cal_ref.fits')
    newh = fits.HDUList([h['primary'],h['sci'],h['err'],h['dq'],h['area']])
    newhref = fits.HDUList([href['primary'],href['sci'],href['err'],href['dq'],href['area']])
    result = fits.diff.FITSDiff(newh,
                              newhref,
                              ignore_keywords = ['DATE','CAL_VER','CAL_VCS','CRDS_VER','CRDS_CTX'],
                              rtol = 0.00001
    )
    assert result.identical, result.report()
