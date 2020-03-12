sudo /etc/init.d/ntp stop 
sudo /usr/sbin/ntpdate $1 
sudo /sbin/hwclock --systohc 
sudo /etc/init.d/ntp start
