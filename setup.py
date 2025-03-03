from setuptools import setup, find_packages

setup(
    name="netwatch",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask==2.0.1',
        'flask-socketio==5.1.1',
        'flask-login==0.5.0',
        'geoip2==4.7.0',
        'flask-wtf==1.0.0',
        'psutil==5.8.0',
        'scapy==2.4.5',
        'gunicorn==20.1.0',
        'eventlet==0.33.0',
        'python-dotenv==0.19.0',
    ],
) 