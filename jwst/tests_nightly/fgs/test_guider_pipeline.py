import os
import pytest

from astropy.io import fits
from jwst.helpers import get_bigdata, require_bigdata, cmp_fitshdr
from jwst.pipeline.calwebb_guider import GuiderPipeline


@require_bigdata
@pytest.mark.parametrize('data_file, args',
    [('jw88600073001_gs-acq1_2016022183837_', dict()),
     ('jw88600073001_gs-id_7_image-', dict()),
     ('jw86600004001_gs-id_1_stacked-', dict()),]
)
def test_GuiderPipeline(data_file, args):
    input_file = get_bigdata('fgs', 'test_guiderpipeline', data_file + 'uncal.fits')
    ref_file = get_bigdata('fgs', 'test_guiderpipeline', data_file + 'cal_ref.fits')
    output_file = data_file + 'cal.fits'

    GuiderPipeline.call(input_file, output_file=output_file, **args)
    cmp_fitshdr(output_file, ref_file)
