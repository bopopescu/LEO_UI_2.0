#!/bin/sh

# This tool is used to update bootloader in system. need root.
# Don't modify this script.
# Any modify may cause the system damage or data lose.

DRIVE=/dev/mmcblk0

echo "[Update uboot files...]"
dd if=/dev/zero of=${DRIVE} bs=512 seek=1536 count=16 >/dev/null

echo 0 > /sys/block/mmcblk0boot0/force_ro

dd if=u-boot.bin of=${DRIVE}boot0 bs=512 skip=2 seek=2 >/dev/null

echo 1 > /sys/block/mmcblk0boot0/force_ro

echo "[Bootrom Update Done]" > /opt/ubootupdate.txt

echo "[Please reboot to use new uboot]"
