from setuptools import setup, find_packages

setup(

    name='gitcheckadd',

    py_modules=["gitcheckadd"],

    package_dir={"": "src"},

    version='0.1',

    description='git check add file format and size',

    author='linxuhua',

    author_email='hualee215@gmail.com',

    url='https://github.com/joelin',

    entry_points={"console_scripts": ["gitcheckadd=gitcheckadd:main"]},

    install_requires=['enum', 'GitPython', 'PyYAML'],

    license="MIT",

)
