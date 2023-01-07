FROM python:3.10.8
WORKDIR /code/

COPY hz_client/requirements.txt .

RUN pip install -r requirements.txt

RUN apt update
RUN apt install -y iputils-ping netcat net-tools
RUN apt install -y inetutils-traceroute
RUN apt install -y iproute2
RUN apt install -y curl telnet dnsutils

COPY hz_client/ .
COPY .env .

# CMD ["nc", "-ul", "8000"]
CMD ["python", "-u", "simplified_test.py"]
