""" Setup file for distutils

"""

from distutils.core import setup

setup(
    name='pymailgun',
    version='1.1',
    author='Tony Sanchez',
    author_email='mail.tsanchez@gmail.com',
    url='https://github.com/cogniteev/pymailgun',
    download_url='https://github.com/cogniteev/pymailgun/archive/master.zip',
    description='A simple mailgun client',
    packages=['pymailgun'],
    license='Apache license version 2.0',
    platforms='OS Independent',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Environment :: Web Environment',
        'Development Status :: 4 - Beta'
    ],
    install_requires='requests>=2.2.1'
)
