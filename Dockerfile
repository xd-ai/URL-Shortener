FROM python:3
RUN apt-get -y update && apt-get -y upgrade
RUN apt-get install -y cron
RUN pip3 install Flask SQLAlchemy Flask-SQLAlchemy flask-restx flask-httpauth psycopg2-binary
COPY crontab /etc/cron.d/cjob
RUN chmod 0644 /etc/cron.d/cjob
ENV PYTHONUNBUFFERED 1
CMD cron -f
