import os
import pytest
from astropy.io import fits
from jwst.helpers import get_bigdata, require_bigdata, cmp_fitshdr
from jwst.saturation.saturation_step import SaturationStep

from ..helpers import add_suffix


@require_bigdata
def test_saturation_miri():
    """

    Regression test of saturation step performed on uncalibrated MIRI data.

    """
    output_file_base, output_file = add_suffix('saturation1_output.fits', 'saturation')

    try:
        os.remove(output_file)
    except:
        pass



    SaturationStep.call(_bigdata+'/miri/test_saturation/jw00001001001_01101_00001_MIRIMAGE_dq_init.fits',
                        output_file=output_file_base, name='saturation'
                        )
    h = fits.open(output_file)
    href = fits.open(_bigdata+'/miri/test_saturation/jw00001001001_01101_00001_MIRIMAGE_saturation.fits')
    newh = fits.HDUList([h['primary'],h['sci'],h['err'],h['pixeldq'],h['groupdq']])
    newhref = fits.HDUList([href['primary'],href['sci'],href['err'],href['pixeldq'],href['groupdq']])
    result = fits.diff.FITSDiff(newh,
                              newhref,
                              ignore_keywords = ['DATE','CAL_VER','CAL_VCS','CRDS_VER','CRDS_CTX'],
                              rtol = 0.00001
    )
    assert result.identical, result.report()
