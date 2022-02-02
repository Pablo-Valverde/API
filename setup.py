from setuptools import setup
from sys import platform
import os

with open("requirements.txt", "r") as requirements_file:
        requirements = [requirement.replace("\n", "") for requirement in requirements_file.readlines()]

if platform == "linux" or platform == "linux2":
        print("Do you wish to install ngrok? (Y/n)")
        selection = input()
        if selection.lower() == "y":
                os.popen('curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null && echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list && sudo apt update && sudo apt install ngrok')

setup(
        name="felaciano_api",
        version="0.0.0",
        author="Pablo Valverde",
        author_email="pabludo8cho@gmail.com",
        description="",
        long_description="",
        long_description_content_type="text/markdown",
        url="https://github.com/Pablo-Valverde/API",
        install_requires=requirements,
        classifiers=[
            "Programming Language :: Python :: 3.9.5",
            "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        ],
)
