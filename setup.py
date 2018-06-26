import fnmatch
import importlib
import os
import pkgutil
import platform
import sys
import verhawk
from ctypes.util import find_library
from distutils.spawn import find_executable
from glob import glob
from os.path import basename
from setuptools import setup, find_packages, Extension, Command
from setuptools.command.test import test as TestCommand
from subprocess import check_call, check_output, CalledProcessError

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
    'verhawk'
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
    'unixODBC': 'odbcinst',
    'mysql': 'mysql',
    'bash': 'bash',
    'tcsh': 'tcsh',
    'zsh': 'zsh',
    'pytest': 'pytest'
}
EXTERN_LIB_REQUIRES = {}


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


def get_version(package):
    module = importlib.import_module(package)
    return verhawk.scanner.Scanner(module).versions[package]


def sanitize_package_name(package):
    '''Sanitize package name by:
        - Converting dashes to underscores
        - Omitting version constraints
    '''
    package = package.replace('-', '_')

    constraints = ' !<>=,'
    for char in constraints:
        pos = package.find(char)
        if pos >= 0:
            package = package[0:pos]
    return package


def get_version_bin(path):
    '''Brute-force the version string out of a program
    '''
    version = None
    version_standards = [
        # GNU
        '--version', '-V',
        # Darwin
        '-version', '-Version',
    ]

    if sys.platform.startswith('win'):
        version_standards = [
            '/version', '/V', '/Version'
        ]

    for version_standard in version_standards:
        cmd = [path, version_standard]
        try:
            version = check_output(cmd).decode()
        except CalledProcessError as cpe:
            # Did not exit gracefully... so on to the next
            continue

        if version:
            version = version.splitlines()[0]
            break

    return version


def get_package(package, hint='python'):
    hints = ['python', 'bin', 'lib']
    result = None

    if hint not in hints:
        raise ValueError('Invalid hint: "{}" (try: {})'.format(hint, ','.join(hints)))

    if hint == 'python':
        try:
            result = os.path.dirname(importlib.import_module(package).__file__)
        except ImportError:
            # result will be None
            pass

    elif hint == 'bin':
        result = find_executable(package)

    elif hint == 'lib':
        result = find_library(package)

    return result


def summary():
    fmt = '    {:.<30s}{:<10} [{}]\n'
    output = '\n\n========= Build Summary =========\n\n'

    # Python packages
    if INSTALL_REQUIRES:
        output += 'Python Dependencies:\n\n'
        output += 'Search prefix: {}\n\n'.format(sys.prefix)
        for name in sorted(INSTALL_REQUIRES):
            name = sanitize_package_name(name)
            location = get_package(name, hint='python')
            state = location == 'Missing' or 'Installed'

            if location:
                ver = get_version(name) or 'Unavailable'

            output += fmt.format(name, state, ver)

    # Binaries
    if EXTERN_BIN_REQUIRES:
        output += '\nExternal Binary Dependencies:\n\n'

        for package, realname in EXTERN_BIN_REQUIRES.items():
            fmt = '    {:.<30s}{:<10}'
            location = get_package(realname, 'bin')
            state = location == 'Missing' or 'Installed'

            if location:
                fmt += ' [{}]\n'
                ver = get_version_bin(realname) or 'Unavailable'
                output += fmt.format(package, state, ver)
            else:
                fmt += '\n'
                output += fmt.format(package, state)

    if TESTS_REQUIRE:
        pass
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
