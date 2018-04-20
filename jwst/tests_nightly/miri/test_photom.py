import os
import pytest
from astropy.io import fits as pf
from jwst.helpers import get_bigdata, require_bigdata, cmp_fitshdr
from jwst.photom.photom_step import PhotomStep

from ..helpers import add_suffix


@require_bigdata
def test_photom_miri():
    """

    Regression test of photom step performed on MIRI imaging data.

    """
    output_file_base, output_file = add_suffix('photom1_output.fits', 'photom')

    try:
        os.remove(output_file)
    except:
        pass



    PhotomStep.call(_bigdata+'/miri/test_photom/jw00001001001_01101_00001_MIRIMAGE_emission.fits',
                    output_file=output_file_base
                    )
    h = pf.open(output_file)
    href = pf.open(_bigdata+'/miri/test_photom/jw00001001001_01101_00001_MIRIMAGE_photom.fits')
    newh = pf.HDUList([h['primary'],h['sci'],h['err'],h['dq'],h['relsens'],h['area']])
    newhref = pf.HDUList([href['primary'],href['sci'],href['err'],href['dq'],href['relsens'],href['area']])
    result = pf.diff.FITSDiff(newh,
                              newhref,
                              ignore_keywords = ['DATE','CAL_VER','CAL_VCS','CRDS_VER','CRDS_CTX'],
                              rtol = 0.00001
    )
    assert result.identical, result.report()
