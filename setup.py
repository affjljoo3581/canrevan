from setuptools import dist, setup, find_packages

# `Cython` is used when installing `kss` library.
dist.Distribution().fetch_build_eggs(['Cython'])

setup(
    name='canrevan',
    version='1.1.3',

    author='Jungwoo Park',
    author_email='affjljoo3581@gmail.com',

    description='Simple Naver News Crawler',
    long_description=open('README.md', 'r', encoding='utf-8').read(),
    long_description_content_type='text/markdown',

    keywords=['naver', 'news', 'dataset', 'nlp'],
    url='https://github.com/affjljoo3581/canrevan',
    license='Apache-2.0',

    package_dir={'': 'src'},
    packages=find_packages('src'),
    python_requires='>=3.6.0',
    install_requires=[
        'tqdm>=4.46.0',
        'kss==1.3.1',
        'bs4',
        'lxml>=4.5.1'
    ],

    entry_points={
        'console_scripts': [
            'canrevan = canrevan:_main'
        ]
    },

    classifiers=[
        'Environment :: Console',
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ]
)
