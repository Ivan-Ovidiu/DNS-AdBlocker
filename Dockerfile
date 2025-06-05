FROM python:3.11

RUN apt-get update && apt-get install -y \
    sudo \
    curl \
    bash \
    dnsutils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

#aici am pus toate librariile de care am nevoie
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


EXPOSE 53/udp
EXPOSE 8080/tcp


CMD ["bash"]