from setuptools import setup

setup(
    name='indexclient',
    use_scm_version={
        'local_scheme': 'dirty-tag',
        'write_to': 'indexclient/_version.py',
    },
    setup_requires=['setuptools_scm'],
    packages=[
        'indexclient',
        'indexclient.parsers',
    ],
    install_requires=[
        'requests>=2.5.2,<3.0.0',
    ],
)
