import os
import pytest
from astropy.io import fits
from jwst.helpers import get_bigdata, require_bigdata, cmp_fitshdr
from jwst.dark_current.dark_current_step import DarkCurrentStep

from ..helpers import add_suffix


@require_bigdata
def test_dark_current_miri2():
    """

    Regression test of dark current step performed on MIRI data.

    """
    suffix = 'dark_current'
    output_file_base, output_file = add_suffix('darkcurrent2_output.fits', suffix)

    try:
        os.remove('output_file')
    except:
        pass

    DarkCurrentStep.call(_bigdata+'/miri/test_dark_step/jw80600012001_02101_00003_mirimage_lastframe.fits',
                         output_file=output_file_base, suffix=suffix
                         )
    h = fits.open(output_file)
    href = fits.open(_bigdata+'/miri/test_dark_step/jw80600012001_02101_00003_mirimage_dark.fits')
    newh = fits.HDUList([h['primary'],h['sci'],h['err'],h['pixeldq'],h['groupdq']])
    newhref = fits.HDUList([href['primary'],href['sci'],href['err'],href['pixeldq'],href['groupdq']])
    result = fits.diff.FITSDiff(newh,
                              newhref,
                              ignore_keywords = ['DATE','CAL_VER','CAL_VCS','CRDS_VER','CRDS_CTX'],
                              rtol = 0.00001
    )
    assert result.identical, result.report()
