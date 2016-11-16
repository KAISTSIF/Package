from distutils.core import setup

setup(
    name='KSIF',
    version='0.1.0',
    packages=['', 'ML', 'core', 'util', 'miner', 'team3', 'tests'],
    package_dir={'': 'KSIF'},
    url='',
    license='KSIF',
    author='Seung Hyeon Yu',
    author_email='rambor12@business.kaist.ac.kr',
    description='Package for investment', requires=['pandas']
)
