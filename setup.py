from distutils.core import setup

setup(
    # Application name:
    name="Autonoe",

    # Version number (initial):
    version="0.1.0",

    # Application author details:
    author="kardigen",
    author_email="kardigen@o2.pl",

    # Packages
    packages=['autonoe'],

    # Include additional files into the package
    include_package_data=False,

    # Details
    url="",

    #
    # license="LICENSE.txt",
    description="BSD",

    # long_description=open("README.txt").read(),

    # Dependent packages (distributions)
    install_requires=[
        "exifread",
    ],
)