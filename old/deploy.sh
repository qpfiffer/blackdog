#!/bin/bash -e

rsync -Paz built/* static data robots.txt favicon.ico blackdog.shithouse.tv:/var/www/blackdog/
