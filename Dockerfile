FROM debian:latest

RUN apt update && apt -y upgrade
RUN apt install -y python3 python3-dev python3-pip python3-psycopg2

RUN mkdir /var/teamlock
RUN touch /var/teamlock/debug.log && \
	touch /var/teamlock/django.log

COPY . /app/
WORKDIR /app/
RUN pip3 install -r requirements.txt
RUN python3 manage.py makemigrations
RUN python3 manage.py migrate

CMD python3 /app/manage.py runserver 0.0.0.0:8000 && tail -f /var/log/teamlock/*.log

