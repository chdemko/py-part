import setuptools


def add_cythonize():
    try:
        from setuptools_cythonize import get_cmdclass

        return get_cmdclass()
    except ModuleNotFoundError:
        return {}


def add_sphinx():
    try:
        from sphinx.setup_command import BuildDoc

        return {"build_sphinx": BuildDoc}
    except ModuleNotFoundError:
        return {}


with open("README.md", "r") as stream:
    long_description = stream.read()

setuptools.setup(
    name="py-part",
    version="0.0.2",
    author="Christophe Demko",
    author_email="chdemko@gmail.com",
    description="An interval library package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chdemko/py-part",
    include_package_data=True,
    package_data={"part": ["__init__.pyi", "py.typed"]},
    packages=["part"],
    license="BSD-3-Clause",
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: BSD License",
        # Specify the OS
        "Operating System :: OS Independent",
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 3 - Alpha",
        # Indicate who your project is intended for
        "Intended Audience :: Developers",
        # Natural language used
        "Natural Language :: English",
    ],
    python_requires=">=3.6",
    install_requires=["sortedcontainers>=2.1"],
    extras_require={
        "docs": [
            "sphinx>=3.0",
            "sphinx_rtd_theme>=0.4",
            "jupyter>=1.0",
            "graphviz>=0.13",
            "nbsphinx>=0.5",
        ],
        "test": [
            "tox>=3.14",
            "doc8",
            "Pygments>=2.5",
            "pylint>=2.4",
            "pep257",
            "mypy",
            "black",
            "pytest-cov",
            "nose2",
        ],
        "build": ["setuptools_cythonize>=1.0"],
    },
    cmdclass={**add_sphinx(), **add_cythonize()},
)
