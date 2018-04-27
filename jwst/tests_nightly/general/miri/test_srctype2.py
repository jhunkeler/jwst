import os
import pytest
from astropy.io import fits as pf
from jwst.srctype.srctype_step import SourceTypeStep

from ..helpers import add_suffix

pytestmark = [
    pytest.mark.usefixtures('_jail'),
    pytest.mark.skipif(not pytest.config.getoption('bigdata'),
                       reason='requires --bigdata')
]

def test_srctype2():
    """

    Regression test of srctype step performed on MIRI LRS slitless data.

    """
    output_file_base, output_file = add_suffix('srctype2_output.fits', 'sourcetypestep')

    try:
        os.remove(output_file)
    except:
        pass



    SourceTypeStep.call(_bigdata+'/miri/test_srctype/jw80600012001_02101_00003_mirimage_flat_field.fits',
                        output_file=output_file_base
                        )
    h = pf.open(output_file)
    href = pf.open(_bigdata+'/miri/test_srctype/jw80600012001_02101_00003_mirimage_srctype.fits')
    newh = pf.HDUList([h['primary'],h['sci'],h['err'],h['dq']])
    newhref = pf.HDUList([href['primary'],href['sci'],href['err'],href['dq']])
    result = pf.diff.FITSDiff(newh,
                              newhref,
                              ignore_keywords = ['DATE','CAL_VER','CAL_VCS','CRDS_VER','CRDS_CTX'],
                              rtol = 0.00001
    )
    assert result.identical, result.report()
