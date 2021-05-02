from setuptools import setup, find_packages

setup(
    name="BQuarium",
    version="0.1",
    install_requires=[
		'pygame>=1.9.3'
    ],
    package_dir={'':'bquarium'},
    author="Mike Sanderson",
    description="A calming Bee Aquarium",
    package_data={
		'': ['*.png', '*.ico']
    },
    scripts=['bquarium/bquarium.py'],
    entry_points={
		'console_scripts':[
			'bquarium = bquarium:main'
		]
    }
)
