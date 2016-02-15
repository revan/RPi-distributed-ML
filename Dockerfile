
FROM resin/raspberrypi2-python:3.4

# Enable systemd
ENV INITSYSTEM on

RUN apt-get update 
RUN apt-get install -y zookeeperd
RUN pip install kazoo

# copy current directory into /app
COPY . /app

CMD ["/app/init.sh"]
