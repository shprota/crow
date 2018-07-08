from setuptools import setup

setup(name='crow_security',
      version='0.2',
      description='Crow security system interface',
      url='http://github.com/shprota/crow',
      author='Shprota',
      author_email='shprota@gmail.com',
      license='MIT',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.2',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
      ],
      keywords='alarm security crow',
      packages=['crow_security'],
      install_requires=[
          'requests', 'aiohttp'],
      zip_safe=False)
