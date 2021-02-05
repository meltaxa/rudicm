#!/bin/bash

# RudiCM bootstrap to install required dependancies.
# Run it as:
#   source bootstrap.sh

activate () {
    . ~/venv/bin/activate
}

chmod u+x bootstrap.sh
chmod u+x rudicm.py
sudo apt -y install python3-pip
sudo pip3 install virtualenv
sudo apt -y install unzip
virtualenv -p python3 ~/venv
activate
pip install --upgrade pip
pip install -r requirements.txt
