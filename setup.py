from setuptools import setup


with open('README.md') as readme:
    long_description = readme.read()

setup(
    name='WSGI-MonkeyType',
    version='1.0.2',
    url='https://github.com/xiachufang/wsgi-monkeytype',
    license='BSD',
    author='xcf',
    author_email='xcf@xiachufang.com',
    description='some monkeytype utils for wsgi application',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=['wsgi_monkeytype'],
    install_requires=[
        'monkeytype',
    ],
    extras_require={
        'mysql': ['mysqlclient', 'DBUtils'],
        'flask': ['Flask']
    },
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ]
)
