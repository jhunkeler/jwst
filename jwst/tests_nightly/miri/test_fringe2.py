import os
import pytest
from astropy.io import fits
from jwst.helpers import get_bigdata, require_bigdata, cmp_fitshdr
from jwst.fringe.fringe_step import FringeStep

from ..helpers import add_suffix


@require_bigdata
def test_fringe_miri2():
    """

    Regression test of fringe performed on MIRI data.

    """
    suffix = 'fringe'
    output_file_base, output_file = add_suffix('fringe2_output.fits', suffix)

    try:
        os.remove(output_file)
    except:
        pass

    FringeStep.call(_bigdata+'/miri/test_fringe/fringe2_input.fits',
                    output_file=output_file_base, suffix=suffix
                    )
    h = fits.open(output_file)
    href = fits.open(_bigdata+'/miri/test_fringe/baseline_fringe2.fits')
    newh = fits.HDUList([h['primary'],h['sci'],h['err'],h['dq']])
    newhref = fits.HDUList([href['primary'],href['sci'],href['err'],href['dq']])
    result = fits.diff.FITSDiff(newh,
                              newhref,
                              ignore_keywords = ['DATE','CAL_VER','CAL_VCS','CRDS_VER','CRDS_CTX'],
                              rtol = 0.00001
    )
    assert result.identical, result.report()
