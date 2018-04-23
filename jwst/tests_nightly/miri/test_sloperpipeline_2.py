import os
import pytest
from astropy.io import fits
from jwst.helpers import get_bigdata, require_bigdata, cmp_fitshdr
from jwst.pipeline.calwebb_detector1 import Detector1Pipeline


@require_bigdata
def test_detector1pipeline2():
    """

    Regression test of calwebb_detector1 pipeline performed on MIRI data.

    """
    step = Detector1Pipeline()
    step.save_calibrated_ramp = True
    step.refpix.odd_even_columns = True
    step.refpix.use_side_ref_pixels = True
    step.refpix.side_smoothing_length=11
    step.refpix.side_gain=1.0
    step.refpix.odd_even_rows = True
    step.jump.rejection_threshold = 250.0
    step.ramp_fit.save_opt = False

    step.run(_bigdata+'/miri/test_sloperpipeline/jw80600012001_02101_00003_mirimage_uncal.fits',
             output_file='jw80600012001_02101_00003_mirimage_rate.fits')

    # Compare the calibrated ramp product
    n_cr = 'jw80600012001_02101_00003_mirimage_ramp.fits'
    h = fits.open( n_cr )
    n_ref = _bigdata+'/miri/test_sloperpipeline/jw80600012001_02101_00003_mirimage_ramp.fits'
    href = fits.open( n_ref )
    newh = fits.HDUList([h['primary'],h['sci'],h['err'],h['groupdq'],h['pixeldq']])
    newhref = fits.HDUList([href['primary'],href['sci'],href['err'],href['groupdq'],href['pixeldq']])
    result = fits.diff.FITSDiff(newh,
                              newhref,
                              ignore_keywords = ['DATE','CAL_VER','CAL_VCS','CRDS_VER','CRDS_CTX'],
                              rtol = 0.00001
    )
    assert result.identical, result.report()

    # Compare the multi-integration countrate image product
    n_int = 'jw80600012001_02101_00003_mirimage_rateints.fits'
    h = fits.open( n_int )
    n_ref = _bigdata+'/miri/test_sloperpipeline/jw80600012001_02101_00003_mirimage_rateints.fits'
    href = fits.open( n_ref )
    newh = fits.HDUList([h['primary'],h['sci'],h['err'],h['dq']])
    newhref = fits.HDUList([href['primary'],href['sci'],href['err'],href['dq']])
    result = fits.diff.FITSDiff(newh,
                              newhref,
                              ignore_keywords = ['DATE','CAL_VER','CAL_VCS','CRDS_VER','CRDS_CTX'],
                              rtol = 0.00001
    )
    assert result.identical, result.report()

    # Compare the countrate image product
    n_rate = 'jw80600012001_02101_00003_mirimage_rate.fits'
    h = fits.open( n_rate )
    n_ref = _bigdata+'/miri/test_sloperpipeline/jw80600012001_02101_00003_mirimage_rate.fits'
    href = fits.open( n_ref )
    newh = fits.HDUList([h['primary'],h['sci'],h['err'],h['dq']])
    newhref = fits.HDUList([href['primary'],href['sci'],href['err'],href['dq']])
    result = fits.diff.FITSDiff(newh,
                              newhref,
                              ignore_keywords = ['DATE','CAL_VER','CAL_VCS','CRDS_VER','CRDS_CTX'],
                              rtol = 0.00001
    )
    assert result.identical, result.report()
