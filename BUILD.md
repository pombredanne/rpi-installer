raspbian-ua-netinst build instructions
======================================

To create an image yourself, you need to have various packages installed on the host machine.
On a Debian system those are the following, excluding packages with priority essential and required:
- git
- curl
- bzip2
- zip
- xz-utils
- gnupg
- kpartx
- dosfstools
- binutils
- bc

The following scripts are used to build the raspbian-ua-netinst installer, listed in the same order they would be used:

 - update.sh - Downloads latest Raspbian packages that will be used to build the installer.
 - build.sh - Builds the installer initramfs and .zip package for Windows/Mac SD card extraction method. Transfer the .zip package to a Windows/Mac computer, then simply unzip it and copy the files onto a FAT formatted SD card.
 - buildroot.sh - Builds the installer SD card image, it requires root privileges and it makes some assumptions like not having any other loop devices in use. You only need to execute this script if you need more than a .zip package. The script produces an .img package and also its bzip2 and xz compressed versions.
 - clean.sh - Remove everything created by above scripts.

update.sh
---------
This script downloads latest required Raspbian packages that will be used to build the installer. The packages to be downloaded are taken from a **pre-defined** list.

First, the archive's public key is downloaded and after successful verification of its fingerprint, it is imported into a newly created `gpg` keyring.

Next, the `Release` file is downloaded. Upon successful verification of its signature (`Release.gpg`) using the previously imported public key, the `firmware` and `main` package lists are looked up:
~~~
SHA256:
 ...
 115d8a933597733fc9567d089c6e234d390eec34adb5deb9f483b0c0073ce96b 12471356 main/binary-armhf/Packages.gz
 ...
 30425fd11b19c0cc2403a0285e66ec4242ac9fee75ca40f8e00d21f01eb9755b 1203 firmware/binary-armhf/Packages.gz
 ...
~~~

Both package lists are downloaded and their checksums verified against the values found in the `Release` file. Once decompressed, its contents is written in a `Packages` file:

~~~
Package: libraspberrypi-bin
Source: raspberrypi-firmware-nokernel
Version: 1.20160523-1~nokernel2
Architecture: armhf
Maintainer: Peter Michael Green <plugwash@raspbian.org>
Installed-Size: 1037
Depends: libraspberrypi0 (= 1.20160523-1~nokernel2), device-tree-compiler
Homepage: https://github.com/raspberrypi/firmware
Priority: extra
Section: firmware/misc
Filename: pool/firmware/r/raspberrypi-firmware-nokernel/libraspberrypi-bin_1.20160523-1~nokernel2_armhf.deb
Size: 253458
SHA256: ad71ae6f678010a45ec26f1bcb8ccae870e8ea189768ea10abe7748f1fd501a1
SHA1: cc2fec77312ea7f9d7d5f4787326fd5260494c38
MD5sum: c86600899abd966ad9ef74f122c40072
Description: Miscellaneous Raspberry Pi utilities
 This package contains various utilities for interacting with the Raspberry
 Pi's VideoCore IV.

 ...
~~~

Finally, all `.deb` files (found in `Packages`) matching the required packages are downloaded into the `packages` directory. As usual, their SHA256 checksums are also verified.

build.sh
---------
Once all required packages are downloaded, this script extracts their binaries to build the installer initramfs.
