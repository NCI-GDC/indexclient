from setuptools import find_packages, setup

setup(
    name="indexclient",
    use_scm_version={
        "local_scheme": "dirty-tag",
        "write_to": "_version.py",
    },
    python_requires=">=2.7,!=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*",
    setup_requires=["setuptools_scm<6"],
    packages=find_packages(),
    package_data= {
        "indexclient": ["py.typed"]
    },
    install_requires=[
        "requests>=2.5",
    ],
    extras_require={"sqlalchemy": ["sqlalchemy<1.4"]},
)
