import os
import pytest
from astropy.io import fits
from jwst.helpers import get_bigdata, require_bigdata, cmp_fitshdr, cmp_gen_hdrkeywords
from jwst.extract_2d.extract_2d_step import Extract2dStep

from ..helpers import add_suffix


@require_bigdata
def test_extract2d_nirspec():
    """

    Regression test of extract_2d step performed on NIRSpec fixed slit data.

    """
    output_file_base, output_file = add_suffix('extract2d1_output.fits', 'extract_2d')
    input_file = get_bigdata('nirspec/test_extract_2d/jw00023001001_01101_00001_NRS1_assign_wcs.fits')
    truth_file = get_bigdata('nirspec/test_extract_2d/jw00023001001_01101_00001_NRS1_extract_2d.fits')


    Extract2dStep.call(output_file=output_file_base, name='extract_2d')

    diff_keys = cmp_gen_hdrkeywords(['primary', 'sci', 'err', 'dq'], limit=5, start=1)

    cmp_fitshdr(output_file, truth_file, keys=diff_keys)

    #newh = fits.HDUList([h['primary'], h[('sci', 1)], h[('err', 1)], h[('dq', 1)],
    #                   h[('sci', 2)], h[('err', 2)], h[('dq', 2)],
    #                   h[('sci', 3)], h[('err', 3)], h[('dq', 3)],
    #                   h[('sci', 4)], h[('err', 4)], h[('dq', 4)],
    #                   h[('sci', 5)], h[('err', 5)], h[('dq', 5)]])
    #newhref = fits.HDUList([href['primary'], href[('sci', 1)], href[('err',1)], href[('dq', 1)],
    #                      href[('sci', 2)], href[('err', 2)], href[('dq', 2)],
    #                      href[('sci', 3)], href[('err', 3)], href[('dq', 3)],
    #                      href[('sci', 4)], href[('err', 4)], href[('dq', 4)],
    #                      href[('sci', 5)], href[('err', 5)], href[('dq', 5)]])
    #result = fits.diff.FITSDiff(newh, newhref,
    #                          ignore_keywords = ['DATE','CAL_VER','CAL_VCS','CRDS_VER','CRDS_CTX'],
    #                          rtol = 0.00001
    #)
    #assert result.identical, result.report()
