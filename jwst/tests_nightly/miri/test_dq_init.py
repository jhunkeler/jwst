import os
import pytest
from astropy.io import fits
from jwst.helpers import get_bigdata, require_bigdata, cmp_fitshdr
from jwst.dq_init.dq_init_step import DQInitStep

from ..helpers import add_suffix


@require_bigdata
def test_dq_init_miri():
    """

    Regression test of dq_init step performed on uncalibrated MIRI data.

    """
    output_file_base, output_file = add_suffix('dqinit1_output.fits', 'dq_init')

    try:
        os.remove(output_file)
    except:
        pass

    DQInitStep.call(_bigdata+'/miri/test_dq_init/jw00001001001_01101_00001_MIRIMAGE_uncal.fits',
                    output_file=output_file_base, name='dq_init'
    )

    h = fits.open(output_file)
    href = fits.open(_bigdata+'/miri/test_dq_init/jw00001001001_01101_00001_MIRIMAGE_dq_init.fits')
    newh = fits.HDUList([h['primary'],h['sci'],h['err'],h['pixeldq'],h['groupdq']])
    newhref = fits.HDUList([href['primary'],href['sci'],href['err'],href['pixeldq'],href['groupdq']])
    result = fits.diff.FITSDiff(newh,
                              newhref,
                              ignore_keywords = ['DATE','CAL_VER','CAL_VCS','CRDS_VER','CRDS_CTX'],
                              rtol = 0.00001
    )
    assert result.identical, result.report()
