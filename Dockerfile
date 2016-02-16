
FROM resin/raspberrypi2-python:3.4

# Enable systemd
ENV INITSYSTEM on

RUN apt-get update 
RUN apt-get install -y zookeeperd
RUN pip install kazoo

COPY . /app
COPY zoo.cfg /etc/zookeeper/conf/zoo.cfg

CMD ["/app/init.sh"]
