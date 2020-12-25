from setuptools import setup, find_packages

setup(
    name='iuaena',
    version='1.0.0',
    url='https://github.com/taevel02/iuaena-py',
    license='MIT',
    author='Taehoon',
    author_email='taevel02@gmail.com',
    description='The real-time monitoring system for IUAENA',
    packages=find_packages(),
    python_requires='>=3',
    install_requires=['requests', 'selenium', 'bs4']
)
