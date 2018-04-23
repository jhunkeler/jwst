import os
import pytest
from astropy.io import fits
from jwst.helpers import get_bigdata, require_bigdata, cmp_fitshdr
from jwst.jump.jump_step import JumpStep

from ..helpers import add_suffix


@require_bigdata
def test_jump_miri():
    """

    Regression test of jump step performed on MIRI data.

    """
    output_file_base, output_file = add_suffix('jump1_output.fits', 'jump')

    try:
        os.remove(output_file)
    except:
        pass



    JumpStep.call(_bigdata+'/miri/test_jump/jw00001001001_01101_00001_MIRIMAGE_linearity.fits',
                  rejection_threshold=200.0,
                  output_file=output_file_base
                  )
    h = fits.open(output_file)
    href = fits.open(_bigdata+'/miri/test_jump/jw00001001001_01101_00001_MIRIMAGE_jump.fits')
    newh = fits.HDUList([h['primary'],h['sci'],h['err'],h['pixeldq'],h['groupdq']])
    newhref = fits.HDUList([href['primary'],href['sci'],href['err'],href['pixeldq'],href['groupdq']])
    result = fits.diff.FITSDiff(newh,
                              newhref,
                              ignore_keywords = ['DATE','CAL_VER','CAL_VCS','CRDS_VER','CRDS_CTX'],
                              rtol = 0.00001
    )
    assert result.identical, result.report()
