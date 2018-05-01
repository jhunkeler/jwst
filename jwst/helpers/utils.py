import os
import re
import requests
from astropy.io import fits

__all__ = ['cmp_fitshdr', 'cmp_gen_hdrkeywords',
           'word_precision_check', 'abspath',
           'download', 'check_url']

RE_URL = re.compile('\w+://\S+')

default_cmp_fitshdr = dict(
    ignore_keywords=['DATE', 'CAL_VER', 'CAL_VCS', 'CRDS_VER', 'CRDS_CTX'],
    keys=['primary', 'sci', 'dq'],
    rtol=0.000001,
    no_assert=False
)


def cmp_fitshdr(left, right, **kwargs):
    """Compare FITS header values using keywords

    Parameters
    ----------
    left, right: str
        The FITS files to compare

    keys: list
        The header keywords to compare `left` and `right`
        (See `defaults_compare` for initial values)

    rtol: float
        The relative difference to allow when comparing two float values either
        in header values, image arrays, or table columns.
        (See `defaults_compare` for initial values)

    no_assert: boolean
        Return result object instead of asserting

    kwargs: dict
        Additional arguments to be passed to `FITSDiff`

    Returns
    -------
    None
        Assert left and right are identical
    """
    assert isinstance(left, str)
    assert isinstance(right, str)

    local_keys = ['keys', 'rtol', 'ignore_keywords', 'no_assert']
    local_args = dict()

    for k in local_keys:
        local_args[k] = kwargs.get(k, default_cmp_fitshdr[k])
        if k in kwargs:
            del kwargs[k]

    assert isinstance(local_args['keys'], list)
    assert isinstance(local_args['rtol'], float)
    assert isinstance(local_args['ignore_keywords'], list)
    assert isinstance(local_args['no_assert'], bool)

    with fits.open(left) as a:
        with fits.open(right) as b:
            result = fits.diff.FITSDiff(fits.HDUList([a[kw] for kw in local_args['keys']]),
                                        fits.HDUList([b[kw] for kw in local_args['keys']]),
                                        ignore_keywords=local_args['ignore_keywords'],
                                        rtol=local_args['rtol'],
                                        **kwargs)

    if local_args['no_assert']:
        return result

    assert result.identical, result.report()


def cmp_gen_hdrkeywords(keys_dynamic, keys_static=['primary'], limit=0, start=0):
    """Generate list of FITS header elements to compare

    TODO: Use correct terminology

    Parameters
    ----------
    fitsobj: HDUList
        TODO

    keys_dynamic: list
        Keywords to be iterated over

    keys_static: list
        Keywords that must exist and will not be changed

    limit: int
        Number of extensions
        Note: 1-indexed

    start: int
        Start with extension number

    Returns
    -------
    output: list
        Keywords to compare

    """
    #assert isinstance(fitsobj, fits.HDUList)
    assert isinstance(keys_static, list)
    assert isinstance(keys_dynamic, list)

    result = keys_static

    if limit and not start:
        start += 1

    for idx in range(start, limit + 1):
        for key in keys_dynamic:
            if not limit:
                result += key
            else:
                result += key, idx

    return result


# Check strings based on words using length precision
def word_precision_check(str1, str2, length=5):
    """Check to strings word-by-word based for word length

    The strings are checked word for word, but only for the first
    `length` characters

    Parameters
    ----------
    str1, str2: str
        The strings to compare

    length: int
        The number of characters in each word to check.

    Returns
    -------
    match: boolean
        True if the strings match
    """
    words1 = str1.split()
    words2 = str2.split()
    if len(words1) != len(words2):
        return False
    for w1, w2 in zip(words1, words2):
        if w1[:length] != w2[:length]:
            break
    else:
        return True
    return False


def test_word_precision_check():
    """Test word_precision_check"""
    s1 = "a b c"
    s2 = "aa bb cc"
    s3 = "aa bb cc dd"
    s4 = "aazz bbzz cczz"

    assert word_precision_check(s1, s1)
    assert not word_precision_check(s1, s2)
    assert word_precision_check(s1, s2, length=1)
    assert not word_precision_check(s2, s3)
    assert word_precision_check(s2, s4, length=2)


def abspath(filepath):
    """Get the absolute file path"""
    return os.path.abspath(os.path.expanduser(os.path.expandvars(filepath)))


def download(url, dest):
    """Simple http/https downloader
    """
    dest = os.path.abspath(dest)

    with requests.get(url, stream=True) as r:
        with open(dest, 'w+b') as data:
            for chunk in r.iter_content(chunk_size=0x4000):
                data.write(chunk)

    return dest


def check_url(url):
    """ Determine if `url` can be resolved without error
    """
    if RE_URL.match(url) is None:
        return False

    r = requests.head(url, allow_redirects=True)
    if r.status_code >= 400:
        return False
    return True


def add_suffix(fname, suffix, range=None):
    """Add suffix to file name

    Parameters
    ----------
    fname: str
        The file name to add the suffix to

    suffix: str
        The suffix to add_suffix

    range: range
        If specified, the set of indexes will be added to the
        outputs.

    Returns
    -------
    fname, fname_with_suffix
        2-tuple of the original file name and name with suffix.
        If `range` is defined, `fname_with_suffix` will be a list.

    """
    fname_root, fname_ext = os.splitext(fname)
    if range is None:
        with_suffix = ''.join([
            fname_root,
            '_',
            suffix,
            fname_ext
        ])
    else:
        with_suffix = []
        for idx in range:
            with_suffix.append(''.join([
                fname_root,
                '_',
                str(idx),
                '_',
                suffix,
                fname_ext
            ]))

    return fname, with_suffix
