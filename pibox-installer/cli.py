import os
import argparse
import sys
import yaml
from backend import catalog
from run_installation import run_installation
from set_path import set_path
from cancel import CancelEvent

class Logger:
    def step(step):
        print("\033[00;34m--> " + step + "\033[00m")

    def err(err):
        print("\033[00;31m" + err + "\033[00m")

    def raw_std(std):
        sys.stdout.write(std)

    def std(std):
        print(std)

set_path()

parser = argparse.ArgumentParser(description="ideascube/kiwix installer for raspberrypi.")
parser.add_argument("-n", "--name", help="name of the box (mybox)", default="mybox")
parser.add_argument("-t", "--timezone", help="timezone (Europe/Paris)", default="Europe/Paris")
parser.add_argument("-w", "--wifi-pwd", help="wifi password (Open)")
parser.add_argument("-k", "--kalite", help="install kalite (fr | en | ar | es)", choices=["fr", "en", "ar", "er"], nargs="*")
parser.add_argument("-z", "--zim-install", help="install zim", nargs="*")
parser.add_argument("-r", "--resize", help="resize image in GiB (5)", type=float, default=5)
parser.add_argument("-c", "--catalog", help="print zim catalog", action="store_true")
parser.add_argument("-s", "--sd", help="sd card device to put the image onto")

args = parser.parse_args()

if args.catalog:
    for catalog in catalog.get_catalogs():
        print(yaml.dump(catalog, default_flow_style=False, default_style=''))
    exit(0)

run_installation(
        name=args.name,
        timezone=args.timezone,
        wifi_pwd=args.wifi_pwd,
        kalite=args.kalite,
        zim_install=args.zim_install,
        size=args.resize,
        logger=Logger,
        cancel_event=CancelEvent(),
        sd_card=args.sd,
        output_file=not args.sd)
