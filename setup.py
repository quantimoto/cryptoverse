from setuptools import setup, find_packages

setup(
    name="cryptoverse",
    version="0.0.1.dev5",
    description="Cryptocurrency focused quantitative finance tools.",
    url="https://github.com/quantimoto/cryptoverse",
    maintainer='Bruteque',
    maintainer_email='quantimoto@brutesque.com',
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 1 - Planning",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Financial",
    ],
    keywords=["cryptocurrency", "quantitative", "finance"],
    license='GPLv3',
    install_requires=[
        'beautifulsoup4==4.6.1',
        'dict-recursive-update==1.0.1',
        'libkeepass==0.2.0',
        'matplotlib==2.2.2',
        'mpl-finance==0.10.0',
        'pandas==0.23.4',
        'pytest==3.4.1',
        'pytest-runner==4.0',
        'requests==2.20.0',
        'retry==0.9.2',
        'termcolor==1.1.0',
        'twine==1.9.1',
    ],
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    entry_points = {
        'console_scripts': [
            'cryptoverse = cryptoverse.__main__:main',
        ],
    },
    zip_safe=True,
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
)
