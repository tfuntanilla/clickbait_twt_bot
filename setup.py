from setuptools import setup

setup(name='Fake clickbait headlines twitter bot',
      version='0.1',
      description='Twitter bot that generates fake clickbait headlines',
      url='https://github.com/trishafuntanilla/fakebuzz',
      author='Trisha Funtanilla',
      author_email='tfuntanilla@scu.edu',
      install_requires=[
          'google-api-python-client',
          'python-twitter',
          'requests',
          'nltk',
          'markovify'
      ])
