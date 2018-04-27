import os
import pytest
from astropy.io import fits
from jwst.pipeline.calwebb_coron3 import Coron3Pipeline

pytestmark = [
    pytest.mark.usefixtures('_jail'),
    pytest.mark.skipif(not pytest.config.getoption('bigdata'),
                       reason='requires --bigdata')
]

def test_coron3_pipeline1(_bigdata):
    """Regression test of calwebb_coron3 pipeline.

    Test will be performed on NIRCam simulated data.
    """
    subdir = os.path.join(_bigdata, 'nircam', 'test_coron3')
    asn_name = 'jw99999-a3001_20170327t121212_coron3_001_asn.json'
    asn_file = os.path.join(subdir, asn_name)
    override_psfmask = os.path.join(subdir, 'jwst_nircam_psfmask_somb.fits')

    step = Coron3Pipeline()
    step.align_refs.override_psfmask = override_psfmask
    step.outlier_detection.wht_type = 'exptime'
    step.outlier_detection.pixfrac = 1.0
    step.outlier_detection.kernel = 'square'
    step.outlier_detection.fillval = 'INDEF'
    step.outlier_detection.nlow = 0
    step.outlier_detection.nhigh = 0
    step.outlier_detection.maskpt = 0.7
    step.outlier_detection.grow = 1
    step.outlier_detection.snr = '4.0 3.0'
    step.outlier_detection.scale = '0.5 0.4'
    step.outlier_detection.backg = 0.0
    step.outlier_detection.save_intermediate_results = False
    step.outlier_detection.resample_data = False
    step.outlier_detection.good_bits = 4
    step.resample.single = False
    step.resample.wht_type = 'exptime'
    step.resample.pixfrac = 1.0
    step.resample.kernel = 'square'
    step.resample.fillval = 'INDEF'
    step.resample.good_bits = 4
    step.resample.blendheaders = True
    step.run(asn_file)

    # Compare psfstack product
    n_cur = 'jw99999-a3001_t1_nircam_f140m-maskbar_psfstack.fits'
    n_ref_name = 'jw99999-a3001_t1_nircam_f140m-maskbar_psfstack_ref.fits'
    n_ref = os.path.join(subdir, n_ref_name)

    h = fits.open(n_cur)
    href = fits.open(n_ref)
    newh = fits.HDUList([h['primary'], h['sci'], h['err'], h['dq']])
    newhref = fits.HDUList([href['primary'], href['sci'],
                         href['err'], href['dq']])
    kws_to_ignore = ['DATE', 'CAL_VER', 'CAL_VCS', 'CRDS_VER', 'CRDS_CTX']

    result = fits.diff.FITSDiff(newh,
                              newhref,
                              ignore_keywords=kws_to_ignore,
                              rtol=0.00001)
    assert result.identical, result.report()

    # Compare psfalign product
    n_cur = 'jw9999947001_02102_00001_nrcb3_a3001_psfalign.fits'
    n_ref_name = 'jw99999-a3001_t1_nircam_f140m-maskbar_psfalign_ref.fits'
    n_ref = os.path.join(subdir, n_ref_name)
    h = fits.open(n_cur)
    href = fits.open(n_ref)
    newh = fits.HDUList([h['primary'], h['sci'], h['err'], h['dq']])
    newhref = fits.HDUList([href['primary'],
                         href['sci'], href['err'], href['dq']])

    result = fits.diff.FITSDiff(newh,
                              newhref,
                              ignore_keywords=kws_to_ignore,
                              rtol=0.00001)
    assert result.identical, result.report()

    # Compare psfsub product
    n_cur = 'jw9999947001_02102_00001_nrcb3_a3001_psfsub.fits'
    n_ref_name = 'jw9999947001_02102_00001_nrcb3_psfsub_ref.fits'
    n_ref = os.path.join(subdir, n_ref_name)

    h = fits.open(n_cur)
    href = fits.open(n_ref)
    newh = fits.HDUList([h['primary'], h['sci'], h['err'], h['dq']])
    newhref = fits.HDUList([href['primary'], href['sci'],
                          href['err'], href['dq']])

    result = fits.diff.FITSDiff(newh,
                              newhref,
                              ignore_keywords=kws_to_ignore,
                              rtol=0.00001)
    assert result.identical, result.report()

    # Compare level-2c product
    n_cur = 'jw9999947001_02102_00001_nrcb3_a3001_crfints.fits'
    n_ref_name = 'jw9999947001_02102_00001_nrcb3_a3001_crfints_ref.fits'
    n_ref = os.path.join(subdir, n_ref_name)

    h = fits.open(n_cur)
    href = fits.open(n_ref)
    newh = fits.HDUList([h['primary'], h['sci'], h['err'], h['dq']])
    newhref = fits.HDUList([href['primary'], href['sci'],
                          href['err'], href['dq']])

    result = fits.diff.FITSDiff(newh,
                              newhref,
                              ignore_keywords=kws_to_ignore,
                              rtol=0.00001)
    assert result.identical, result.report()

    n_cur = 'jw9999947001_02102_00002_nrcb3_a3001_crfints.fits'
    h = fits.open(n_cur)
    n_ref = os.path.join(subdir,
                        'jw9999947001_02102_00002_nrcb3_a3001_crfints_ref.fits')

    href = fits.open(n_ref)
    newh = fits.HDUList([h['primary'], h['sci'], h['err'], h['dq']])
    newhref = fits.HDUList([href['primary'], href['sci'],
                          href['err'], href['dq']])
    result = fits.diff.FITSDiff(newh,
                              newhref,
                              ignore_keywords=kws_to_ignore,
                              rtol=0.00001)
    assert result.identical, result.report()

    # Compare i2d product
    n_cur = 'jw99999-a3001_t1_nircam_f140m-maskbar_i2d.fits'
    n_ref = os.path.join(subdir,
                         'jw99999-a3001_t1_nircam_f140m-maskbar_i2d_ref.fits')

    h = fits.open(n_cur)
    href = fits.open(n_ref)

    newh = fits.HDUList([h['primary'], h['sci'],
                       h['con'], h['wht'], h['hdrtab']])
    newhref = fits.HDUList([href['primary'], href['sci'],
                          href['con'], href['wht'], href['hdrtab']])
    result = fits.diff.FITSDiff(newh,
                              newhref,
                              ignore_keywords=kws_to_ignore,
                              ignore_fields=kws_to_ignore,
                              rtol=0.00001)
    assert result.identical, result.report()
