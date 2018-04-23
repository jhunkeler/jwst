import os
import pytest
from astropy.io import fits
from jwst.helpers import get_bigdata, require_bigdata, cmp_fitshdr
from jwst.refpix.refpix_step import RefPixStep

from ..helpers import add_suffix


@require_bigdata
def test_refpix_miri2():
    """

    Regression test of refpix step performed on MIRI data.

    """
    input_file = get_bigdata('miri/test_bias_drift/jw00025001001_01107_00001_MIRIMAGE_saturation.fits')
    ref_file = get_bigdata('miri/test_bias_drift/jw00025001001_01107_00001_MIRIMAGE_bias_drift.fits')
    output_file_base, output_file = add_suffix('refpix2_output.fits', 'refpix')
    diff_keys = ['primary', 'sci', 'err', 'pixeldq', 'groupdq']

    RefPixStep.call(input_file,
                    use_side_ref_pixels=False, side_smoothing_length=10, side_gain=1.0,
                    output_file=output_file_base)

    cmp_fitshdr(output_file, ref_file, diff_keys)
