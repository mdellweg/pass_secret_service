from setuptools import setup  # pragma: no cover


def read_file(file_name):
    with open(file_name) as f:
        return f.read()


setup(  # pragma: no cover
    name='pass_secret_service',
    version='0.1a0',
    description=read_file('README.md'),
    license=read_file('LICENSE'),
    author='Matthias Dellweg',
    author_email='2500@gmx.de',
    url='https://github.com/mdellweg/pass_secret_service',
    packages=[
        'pass_secret_service',
        'pass_secret_service.common',
        'pass_secret_service.interfaces',
    ],
    install_requires=[
        'decorator',
        'pygobject',
        'pydbus',
        'click',
        'pypass',
        'simplejson',
    ],
    entry_points='''
        [console_scripts]
        pass_secret_service=pass_secret_service:main
    ''',
)

#  vim: set tw=160 sts=4 ts=8 sw=4 ft=python et noro norl cin si ai :
