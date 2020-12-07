FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app
COPY ./  ./

RUN apt -y update && apt -y upgrade
RUN apt install -y unzip python3 python3-pip
RUN apt install -y /app/google-chrome-stable_current_amd64.deb
RUN pip3 install  --upgrade pip
RUN pip3 install -r /app/requirements.txt
RUN wget  https://chromedriver.storage.googleapis.com/87.0.4280.88/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip && \
    mv chromedriver /usr/local/bin/ 

CMD ["python3", "app.py"]