FROM python:3.10
WORKDIR /usr/src/shortener
RUN apt-get update && apt-get install -y python3-dev python3-pip
RUN apt-get install -y cron
RUN pip3 install Flask SQLAlchemy Flask-SQLAlchemy flask-restx flask-httpauth psycopg2-binary
COPY crontab /etc/cron.d/cjob
COPY . .
RUN chmod 0644 /etc/cron.d/cjob
ENV PYTHONUNBUFFERED 1
CMD cron -f
