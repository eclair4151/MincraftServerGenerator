#!/usr/bin/python
import os
from optparse import OptionParser
import json
from urllib import urlopen, urlretrieve


def _parse_options():
    """
    Parse the command line arguments for script
    """
    try:
        parser = OptionParser(usage='%prog [Options]', version='1.0',)
        parser.add_option(
            '-l', '--location',
            dest='location',
            help='Location of the new server folder'
            )

        parser.add_option(
            '-s', '--snapshot',
            action="store_true",
            default=False,
            dest='snapshot',
            help='Whether the server should download a snapshot'
        )

        parser.add_option(
            '', '--start',
            dest='start',
            action="store_true",
            default=False,
            help='Start the server once its created'
        )

        options, args = parser.parse_args()
        return options, args
    except Exception as e:
        print("Exception while parsing arguments: " + str(e))



options, args = _parse_options()

if not options.location:
    print("Error: Location is required")
    exit(0)

location = os.path.abspath(options.location)
if not os.path.exists(location):
    os.mkdir(location)

os.chdir(location)
print("Generating server in " + location)

url = "https://launchermeta.mojang.com/mc/game/version_manifest.json"
response = urlopen(url)
res = response.read()
data = json.loads(res.decode('UTF-8'))

if options.snapshot:
    minecraft_ver = data['latest']['snapshot']
else:
    minecraft_ver = data['latest']['release']

print("Creating server for version " + minecraft_ver)

for version in data['versions']:
    if version['id'] == minecraft_ver:
        jsonlink = version['url']
        jarres = urlopen(jsonlink).read()
        jardata = json.loads(jarres.decode('UTF-8'))
        link = jardata['downloads']['server']['url']
        print('Downloading jar from ' + link)
        urlretrieve(link, 'minecraft_server.jar')
        break


print("Generating eula")

eula = open('eula.txt', 'w+')
eula.write("eula=true\n")
eula.close()

print("Generating start script")
start = open('start.sh', 'w+')
start.write("#!/bin/bash\n\nscreen -S minecraft java -Xmx5120M -Xms5120M -jar minecraft_server.jar\n")
start.close()
os.chmod('start.sh', 0755)

if options.start:
    print("Starting server")
    os.system("./start.sh")


