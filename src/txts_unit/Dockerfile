FROM python:3.10.8
WORKDIR /txts_unit/

COPY requirements.txt .
RUN pip install -r requirements.txt

RUN apt-get update
RUN apt-get install -y iputils-ping
RUN apt-get install -y inetutils-traceroute
RUN apt-get install -y iproute2
RUN apt-get install -y curl telnet dnsutils

COPY . .

WORKDIR ./test

CMD ["python", "-u", "simplified_test.py"]
