import os
import pytest
from astropy.io import fits
from jwst.helpers import get_bigdata, require_bigdata, cmp_fitshdr, cmp_gen_hdrkeywords
from jwst.pipeline.calwebb_spec2 import Spec2Pipeline


@require_bigdata
def test_miri_lrs_slit_1b():
    """

    Regression test of calwebb_spec2 pipeline performed on a single
    MIRI LRS fixed-slit exposure with multiple integrations.

    """
    input_file = get_bigdata('pipelines/jw00035001001_01101_00001_MIRIMAGE_rateints.fits')

    step = Spec2Pipeline(name='Spec2Pipeline')
    step.save_bsub=True,
    step.save_results=True
    step.resample_spec.save_results = True
    step.cube_build.save_results = True
    step.extract_1d.save_results = True
    step.run(input_file)


    n_cr = 'jw00035001001_01101_00001_MIRIMAGE_cal.fits'
    n_ref = get_bigdata('pipelines/jw00035001001_01101_00001_MIRIMAGE_calints_ref.fits')
    diff_keys = ['primary', 'sci', 'err', 'dq', 'relsens']
    cmp_fitshdr(n_cr, n_ref, keys=diff_keys)

    n_cr = 'jw00035001001_01101_00001_MIRIMAGE_x1d.fits'
    n_ref = get_bigdata('pipelines/jw00035001001_01101_00001_MIRIMAGE_x1dints_ref.fits')
    diff_keys = cmp_gen_hdrkeywords(['extract1d'], limit=4)
    cmp_fitshdr(n_cr, n_ref, keys=diff_keys)
