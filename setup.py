from setuptools import setup, find_packages

version='1.1pinterest1'

setup(
    name='pyres',
    version=version,
    description='Python resque clone',
    author='Matt George',
    author_email='mgeorge@gmail.com',
    maintainer='Matt George',
    license='MIT',
    url='http://github.com/binarydud/pyres',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    download_url='http://pypi.python.org/packages/source/p/pyres/pyres-%s.tar.gz' % version,
    include_package_data=True,
    package_data={'resweb': ['templates/*.mustache','media/*']},
    entry_points = """\
    [console_scripts]
    pyres_manager=pyres.scripts:pyres_manager
    pyres_scheduler=pyres.scripts:pyres_scheduler
    pyres_web=pyres.scripts:pyres_web
    pyres_worker=pyres.scripts:pyres_worker
    """,
    install_requires=[
        'simplejson==2.2.1',
        'Flask==0.8',
        'redis==2.4.10',
        'setproctitle>=1.0'
    ],
    classifiers = [
            'Development Status :: 4 - Beta',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Programming Language :: Python'],
)
