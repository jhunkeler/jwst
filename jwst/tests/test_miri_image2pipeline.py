import os

import pytest
from astropy.io import fits
from ci_watson.artifactory_helpers import get_bigdata

from jwst.pipeline import Image2Pipeline
from jwst.pipeline.collect_pipeline_cfgs import collect_pipeline_cfgs
from .helpers import fitsdiff_default_args


@pytest.fixture(scope="module")
def run_pipeline(request, config_access, jail):
    inputs_root, results_root = config_access
    envopt = request.config.getoption("env")
    input_data = get_bigdata(inputs_root, envopt, 'miri',
        'test_image2pipeline', 'jw00001001001_01101_00001_mirimage_rate.fits')

    collect_pipeline_cfgs('config')
    config_file = os.path.join('config', 'calwebb_image2.cfg')
    Image2Pipeline.call(input_data, config_file=config_file)

    truth_data = get_bigdata(inputs_root, envopt, )

    return jail


@pytest.mark.parametrize("output",
    [
        'jw00001001001_01101_00001_mirimage_cal.fits',
        'jw00001001001_01101_00001_mirimage_i2d.fits',
    ],
)
def test_miri_image2pipeline(run_pipeline, output):
    """
    Regression test of calwebb_image2 pipeline performed on MIRI data.
    """
    result = fits.diff.FITSDiff(
        output,
        output,
        **fitsdiff_default_args,
    )
    assert result.identical, result.report()
