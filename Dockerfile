FROM python:3.9.6

RUN apt update && apt upgrade -y && apt install cron vim -y

WORKDIR /app

COPY . /app
COPY crontab /etc/cron.d/crontab
RUN chmod 0644 /etc/cron.d/crontab
RUN /usr/bin/crontab /etc/cron.d/crontab

RUN cd neptunepy-master && python setup.py install

RUN pip install -r requirements.txt

RUN chmod +x /app/check_attackers.py

CMD [ "cron", "-f" ]
