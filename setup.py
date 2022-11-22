from setuptools import setup
from setuptools import find_packages

setup(
    name="Federico-Pietrocola2022-3",
    verion="0.1.1",
    description="Senolysis quantification using nuclei segmentation",
    py_modules=[
        "gui_senolysis",
        "senolysis_analysis",
        "senolysis_functions",
        "senolysis_main",
    ],
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
        "tqdm_joblib",
        "joblib",
    ],
    entry_points={
        "console_scripts": [
            "senolysisprogram=senolysis_main:main",
        ]
    },
)
