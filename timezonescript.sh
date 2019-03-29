# to avoid entering the timezone in the docker building step
# set noninteractive installation
export DEBIAN_FRONTEND=noninteractive
#install tzdata package
apt-get install -y tzdata
# set your timezone
ln -fs /usr/share/zoneinfo/Europe/London /etc/localtime
dpkg-reconfigure --frontend noninteractive tzdata
