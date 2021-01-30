from setuptools import setup


def read_file(file_name):
    with open(file_name) as f:
        return f.read()


setup(
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
        'click',
        'cryptography',
        'dbus_next',
        'decorator',
        'pypass',
    ],
    entry_points='''
        [console_scripts]
        pass_secret_service=pass_secret_service:main
    ''',
)
