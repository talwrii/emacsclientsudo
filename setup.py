import setuptools
import os

HERE = os.path.dirname(__file__)

setuptools.setup(
    name='emacsclientsudo',
    version="0.1.0",
    author='Tal Wrii',
    author_email='talwrii@gmail.com',
    description='',
    license='GPLv3',
    keywords='',
    url='',
    packages=['emacsclientsudo'],
    long_description='See https://github.com/talwrii/emacsclientsudo',
    entry_points={
        'console_scripts': ['emacsclientsudo=emacsclientsudo.emacsclientsudo:main']
    },
    classifiers=[
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)"
    ],
    test_suite='nose.collector',
    install_requires=['sexpdata']
)
