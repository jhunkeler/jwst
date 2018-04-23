import os
import pytest
from astropy.io import fits
from jwst.helpers import get_bigdata, require_bigdata, cmp_fitshdr
from jwst.ramp_fitting.ramp_fit_step import RampFitStep

from ..helpers import add_suffix


@require_bigdata
def test_ramp_fit_miri2():
    """

    Regression test of ramp_fit step performed on MIRI data.

    """
    output_file_base, output_files = add_suffix('rampfit2_output.fits', 'rampfit', list(range(2)))

    try:
        for output_file in output_files:
            os.remove(output_file)
        os.remove("rampfit2_opt_out_fitopt.fits")
    except:
        pass

    RampFitStep.call(_bigdata+'/miri/test_ramp_fit/jw80600012001_02101_00003_mirimage_jump.fits',
                      save_opt=True,
                      opt_name='rampfit2_opt_out.fits',
                      output_file=output_file_base
                      )

    # compare primary output
    n_priout = output_files[0]
    h = fits.open( n_priout )
    n_priref = _bigdata+'/miri/test_ramp_fit/jw80600012001_02101_00003_mirimage_ramp.fits'
    href = fits.open( n_priref )
    newh = fits.HDUList([h['primary'],h['sci'],h['err'],h['dq']])
    newhref = fits.HDUList([href['primary'],href['sci'],href['err'],href['dq']])
    result = fits.diff.FITSDiff(newh,
                              newhref,
                              ignore_keywords = ['DATE','CAL_VER','CAL_VCS','CRDS_VER','CRDS_CTX'],
                              rtol = 0.00001
    )
    assert result.identical, result.report()

    # compare integration-specific output
    n_intout = output_files[1]
    h = fits.open( n_intout )
    n_intref = _bigdata+'/miri/test_ramp_fit/jw80600012001_02101_00003_mirimage_int.fits'
    href = fits.open( n_intref )
    newh = fits.HDUList([h['primary'],h['sci'],h['err'],h['dq']])
    newhref = fits.HDUList([href['primary'],href['sci'],href['err'],href['dq']])
    result = fits.diff.FITSDiff(newh,
                              newhref,
                              ignore_keywords = ['DATE','CAL_VER','CAL_VCS','CRDS_VER','CRDS_CTX'],
                              rtol = 0.00001
    )
    assert result.identical, result.report()

    # compare optional output
    n_optout = 'rampfit2_opt_out_fitopt.fits'
    h = fits.open( n_optout )
    n_optref = _bigdata+'/miri/test_ramp_fit/jw80600012001_02101_00003_mirimage_opt.fits'
    href = fits.open( n_optref )
    newh = fits.HDUList([h['primary'],h['slope'],h['sigslope'],h['yint'],h['sigyint'],h['pedestal'],h['weights'],h['crmag']])
    newhref = fits.HDUList([href['primary'],href['slope'],href['sigslope'],href['yint'],href['sigyint'],href['pedestal'],href['weights'],href['crmag']])
    result = fits.diff.FITSDiff(newh,
                              newhref,
                              ignore_keywords = ['DATE','CAL_VER','CAL_VCS','CRDS_VER','CRDS_CTX'],
                              rtol = 0.00001
    )
    assert result.identical, result.report()
