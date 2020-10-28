import io
import os
from setuptools import setup, find_packages

with io.open("README.rst", "rt", encoding="utf8") as f:
    readme = f.read()

setup(
    name='Poultry Geek',
    version="1.0.0",
    # url="http://flask.pocoo.org/docs/tutorial/",
    license="BSD",
    maintainer="p92supeg",
    maintainer_email="p92supeg@uco.es",
    description="The best poultry aplication ever",
    long_description=readme,
    packages=find_packages(),
    include_package_data=True,
    # zip_safe=False,
    install_requires=[
        'flask',
    ],
    # extras_require={"test": ["pytest", "coverage"]},
)