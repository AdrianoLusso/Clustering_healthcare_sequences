from setuptools import setup, find_packages

requirements = open("requirements.txt").readlines()
requirements = [r.strip() for r in requirements]

setup(
    name='ml_application_suite',
    version='0.1',
    description='The MVP of a suite of machine learning applications for SOSUNC.',
    author='Adriano Lusso',
    author_email='lussoadriano@gmail.com',
    packages=find_packages(where='.'),
    install_requires=requirements,
    license='MIT',
    keywords="machine learning suite",
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)