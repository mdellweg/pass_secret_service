from setuptools import setup  # pragma: no cover

setup(  # pragma: no cover
    name='pass_secret_service',
    version=0.1,
    py_modules='pass_secret_service',
    install_requires=[
        'pydbus',
        'click',
        'pypass',
    ],
    entry_points='''
        [console_scripts]
        pass_secret_service=pass_secret_service:main
    ''',
)

#  vim: set tw=160 sts=4 ts=8 sw=4 ft=python et noro norl cin si ai :
