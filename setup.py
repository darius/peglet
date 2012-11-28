from distutils.core import setup

version = '0.1.0'

setup(name = 'Peglet',
      version = version,
      author = 'Darius Bacon',
      author_email = 'darius@wry.me',
      py_modules = ['peglet'],
      url = 'https://github.com/darius/peglet',
      description = "Robinson Crusoe's parsing package.",
      long_description = open('README.rst').read(),
      license = 'GNU General Public License (GPL)',
      classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
#        'Programming Language :: Python :: 2.5',  XXX try it
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Interpreters',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing',
        ],
      keywords = 'parsing',
      )
