from setuptools import setup, find_packages

setup(
    name='aws_kinesis_producer_benchmark',
    version='0.0.1',
    description='Script for benchmarking AWS Kinesis Streams producer strategies',
    url='https://github.com/sjakthol/aws-kinesis-producer-benchmark',
    author='Sami Jaktholm',
    author_email='sjakthol@outlook.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='aws kinesis producer benchmark',
    install_requires=['boto3', 'pyformance'],
    scripts=['kinesis-producer.py']
)
