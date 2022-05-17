from setuptools import setup
from setuptools import find_packages

setup(
    name="Federico-Pietrocola2022-3",
    verion="0.0.1",
    description="Senescence quantification",
    py_modules=["main", "functions",'gui'],
    package_dir={"": "src"},
    author_email="robert.welch@scilifelab.se",
    author="Robert Welch",
    url="https://github.com/BIIFSweden/Federico-Pietrocola2022-3",
    packages=find_packages(","),
    install_requires=[
        "matplotlib",
        "numpy",
        "pandas",
        "scikit-image",
        "nd2reader",
        "tk",
        "slicerator",
        "openpyxl",
    ],
)
