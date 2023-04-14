FROM python:3.10.8
WORKDIR /code/

COPY timestamper/requirements.txt .

RUN pip install -r requirements.txt

RUN apt update
RUN apt install -y iputils-ping netcat net-tools
RUN apt install -y inetutils-traceroute
RUN apt install -y iproute2
RUN apt install -y curl telnet dnsutils


COPY timestamper/ .
# COPY .env .

CMD ["python", "-u", "timestamper.py"]
