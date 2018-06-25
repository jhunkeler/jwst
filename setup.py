import fnmatch
import importlib
import os
import pkgutil
import platform
import sys
from distutils.spawn import find_executable
from glob import glob
from os.path import basename
from setuptools import setup, find_packages, Extension, Command
from setuptools.command.test import test as TestCommand
from subprocess import check_call, CalledProcessError

try:
    from numpy import get_include as np_include
except ImportError:
    print('numpy is missing, please install it.')
    exit(1)

# hack building the sphinx docs with C source
from setuptools.command.build_ext import build_ext


if sys.version_info < (3, 5):
    error = """
    JWST 0.9+ does not support Python 2.x, 3.0, 3.1, 3.2, 3.3 or 3.4.
    Beginning with JWST 0.9, Python 3.5 and above is required.

    This may be due to an out of date pip

    Make sure you have pip >= 9.0.1.

    """
    sys.exit(error)


try:
    from sphinx.cmd.build import build_main
    from sphinx.setup_command import BuildDoc

    class BuildSphinx(BuildDoc):
        """Build Sphinx documentation after compiling C source files"""

        description = 'Build Sphinx documentation'

        def initialize_options(self):
            BuildDoc.initialize_options(self)

        def finalize_options(self):
            BuildDoc.finalize_options(self)

        def run(self):
            build_cmd = self.reinitialize_command('build_ext')
            build_cmd.inplace = 1
            self.run_command('build_ext')
            build_main(['-b', 'html', './docs', './docs/_build/html'])

except ImportError:
    class BuildSphinx(Command):
        user_options = []

        def initialize_options(self):
            pass

        def finalize_options(self):
            pass

        def run(self):
            print('!\n! Sphinx is not installed!\n!', file=sys.stderr)
            exit(1)


NAME = 'jwst'
SCRIPTS = [s for s in glob('scripts/*') if basename(s) != '__pycache__']
PACKAGE_DATA = {
    '': [
        '*.fits',
        '*.txt',
        '*.inc',
        '*.cfg',
        '*.csv',
        '*.yaml',
        '*.json'
    ]
}
INSTALL_REQUIRES=[
    'asdf',
    'astropy>=3.0',
    'crds',
    'drizzle',
    'gwcs',
    'jsonschema',
    'namedlist',
    'numpy>=1.11',
    'scipy',
    'spherical-geometry',
    'six',
    'stsci.tools',
    'stsci.image',
    'stsci.imagestats',
    'stsci.convolve',
    'stsci.stimage',
    'photutils',
    'verhawk',
]
EXTRAS_REQUIRE={
    'ephem': ['pymssql', 'jplephem'],
}
TESTS_REQUIRE=[
    'pytest',
    'pytest-remotedata',
    'requests_mock',
]
EXTERN_BIN_REQUIRES = {
        'freetds': 'tsql',
        'unixodbc': 'odbcinst',
        'mysql': 'mysql',
}

def get_transforms_data():
    # Installs the schema files in jwst/transforms
    # Because the path to the schemas includes "stsci.edu" they
    # can't be installed using setuptools.
    transforms_schemas = []
    root = os.path.join(NAME, 'transforms', 'schemas')
    for node, dirs, files in os.walk(root):
        for fname in files:
            if fname.endswith('.yaml'):
                transforms_schemas.append(
                    os.path.relpath(os.path.join(node, fname), root))
    # In the package directory, install to the subdirectory 'schemas'
    transforms_schemas = [os.path.join('schemas', s) for s in transforms_schemas]
    return transforms_schemas


transforms_schemas = get_transforms_data()
PACKAGE_DATA['jwst.transforms'] = transforms_schemas


class PyTest(TestCommand):

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = [NAME]

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        try:
            import pytest
        except ImportError:
            print('Unable to run tests...')
            print('To continue, please install "pytest":')
            print('    pip install pytest')
            exit(1)

        errno = pytest.main(self.pytest_args)
        sys.exit(errno)

def find_library(name):
    if not name:
        return None

    prefix = sys.prefix
    dynamic_link_env = [
        # Linux
        'LD_LIBRARY_PATH',
        # Darwin
        'DYLD_LIBRARY_PATH',
        'DYLD_FALLBACK_LIBRARY_PATH',
        # Windows
        'LIBRARY_PATH',
        'PATH'
    ]
    libexts = [
        'so',
        'dylib',
        'dll',
    ]
    libdirs = [
        os.path.join(prefix, 'lib'),
        os.path.join(prefix, 'lib64'),
    ]

    # Search for shared libraries beyond Python's installation prefix
    for dlvar in dynamic_link_env:
        result = os.environ.get(dlvar, '')
        if result:
            libdirs += result.split(os.pathsep)

    if not name.startswith('lib'):
        name = ''.join(['lib', name])

    for libdir in [x for x in libdirs if os.path.exists(x)]:
        for libext in libexts:
            ext = '*.'.join(['', libext])
            for root, dirs, files in os.walk(libdir):
                for fname in files:
                    fname_no_ext = fname.split('.', 1)[0]
                    if fname_no_ext == name:
                        if fnmatch.fnmatch(fname, ext):
                            return root, \
                                   os.path.basename(fname), \
                                   fname_no_ext
    return None


def summary():
    from verhawk.scanner import Scanner

    stop_char = ' !<>='
    fmt = '    {:.<30s}{:<10} @{}\n'
    vh = None
    output = '\n\n========= Build Summary =========\n\n'

    # Python packages
    output += '[REQUIRED] Dependencies:\n\n'
    for name in sorted(INSTALL_REQUIRES):
        status = 'Missing'
        name = name.replace('-', '_')

        # Sanitize package name omitting version constraints
        for ch in stop_char:
            pos = name.find(ch)
            if pos >= 0:
                name = name[0:pos]


        module = importlib.import_module(name)
        vh = Scanner(module).versions

        if vh:
            status = 'Installed'

        output += fmt.format(name, status, vh[name] or 'Unknown')

    output += '\n[OPTIONAL] Dependencies:\n\n'

    # Binaries
    fmt = '    {:.<30s}{:<10}\n'
    for key, value in EXTERN_BIN_REQUIRES.items():
        status = find_executable(value) == 'Installed' or 'Missing'
        output += fmt.format(key, status)

    print(output)


if not pkgutil.find_loader('relic'):
    relic_local = os.path.exists('relic')
    relic_submodule = (relic_local and
                       os.path.exists('.gitmodules') and
                       not os.listdir('relic'))
    try:
        if relic_submodule:
            check_call(['git', 'submodule', 'update', '--init', '--recursive'])
        elif not relic_local:
            check_call(['git', 'clone', 'https://github.com/spacetelescope/relic.git'])

        sys.path.insert(1, 'relic')
    except CalledProcessError as e:
        print(e)
        exit(1)

import relic.release

version = relic.release.get_info()
relic.release.write_template(version, NAME)

entry_points = dict(asdf_extensions=['jwst_pipeline = jwst.transforms.jwextension:JWSTExtension',
                                     'model_extensions = jwst.datamodels.extension:BaseExtension'])

setup(
    name=NAME,
    version=version.pep386,
    author='OED/SSB, etc',
    author_email='help@stsci.edu',
    description='JWST',
    url='http://ssb.stsci.edu',
    license='BSD',
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.5',
    scripts=SCRIPTS,
    packages=find_packages(),
    package_data=PACKAGE_DATA,
    ext_modules=[
        Extension('jwst.tweakreg.chelp',
                  glob('src/tweakreg/*.c'),
                  include_dirs=[np_include()],
                  define_macros=[('NUMPY', '1')]),
    ],
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    tests_require=TESTS_REQUIRE,
    cmdclass={
        'test': PyTest,
        'build_sphinx': BuildSphinx
    },
    entry_points=entry_points,
)

summary()
