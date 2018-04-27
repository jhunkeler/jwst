import os
import pytest
from astropy.io import fits as pf
from jwst.jump.jump_step import JumpStep

from ..helpers import add_suffix

pytestmark = [
    pytest.mark.usefixtures('_jail'),
    pytest.mark.skipif(not pytest.config.getoption('bigdata'),
                       reason='requires --bigdata')
]

def test_jump_miri2(_bigdata):
    """

    Regression test of jump step performed on MIRI data.

    """
    output_file_base, output_file = add_suffix('jump2_output.fits', 'jump')

    try:
        os.remove(output_file)
    except:
        pass



    JumpStep.call(_bigdata+'/miri/test_jump/jw80600012001_02101_00003_mirimage_dark.fits',
                  rejection_threshold=25.0,
                  output_file=output_file_base
                  )
    h = pf.open(output_file)
    href = pf.open(_bigdata+'/miri/test_jump/jw80600012001_02101_00003_mirimage_jump.fits')
    newh = pf.HDUList([h['primary'],h['sci'],h['err'],h['pixeldq'],h['groupdq']])
    newhref = pf.HDUList([href['primary'],href['sci'],href['err'],href['pixeldq'],href['groupdq']])
    result = pf.diff.FITSDiff(newh,
                              newhref,
                              ignore_keywords = ['DATE','CAL_VER','CAL_VCS','CRDS_VER','CRDS_CTX'],
                              rtol = 0.00001
    )
    assert result.identical, result.report()
