from setuptools import setup, find_packages

setup(
    name="cryptoverse",
    version="0.0.1.dev3",
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
        'requests',
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
