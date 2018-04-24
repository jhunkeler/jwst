import os
import pytest
from astropy.io import fits
from jwst.helpers import get_bigdata, require_bigdata, cmp_fitshdr
from jwst.flatfield.flat_field_step import FlatFieldStep

from ..helpers import add_suffix


@require_bigdata
def test_flat_field_miri2():
    """

    Regression test of flat_field step performed on MIRI data.

    """
    output_file_base, output_file = add_suffix('flatfield2_output.fits', 'flat_field')

    try:
        os.remove(output_file)
    except:
        pass



    FlatFieldStep.call(_bigdata+'/miri/test_flat_field/jw80600012001_02101_00003_mirimage_assign_wcs.fits',
                       output_file=output_file_base, name='flat_field'
                       )
    h = fits.open(output_file)
    href = fits.open(_bigdata+'/miri/test_flat_field/jw80600012001_02101_00003_mirimage_flat_field.fits')
    newh = fits.HDUList([h['primary'],h['sci'],h['err'],h['dq']])
    newhref = fits.HDUList([href['primary'],href['sci'],href['err'],href['dq']])
    result = fits.diff.FITSDiff(newh,
                              newhref,
                              ignore_keywords = ['DATE','CAL_VER','CAL_VCS','CRDS_VER','CRDS_CTX'],
                              rtol = 0.00001
    )
    assert result.identical, result.report()
