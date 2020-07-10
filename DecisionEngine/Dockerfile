# pull official base image
FROM python:3.8.3-buster
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*
RUN pip install pandas

RUN apt-get update && apt-get install nginx vim -y --no-install-recommends
COPY nginx.default /etc/nginx/sites-available/default
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log


# set work directory
WORKDIR /opt/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .


RUN pip install -r requirements.txt --cache-dir /opt/app/pip_cache
RUN chown -R www-data:www-data /opt/app

# copy project
COPY . .

EXPOSE 8000
#STOPSIGNAL SIGTERM
RUN chmod -R 755 start-server.sh
RUN chown -R www-data:www-data /opt/app/drdecisions
RUN chown www-data:www-data /opt/app/drdecisions/db.sqlite3

STOPSIGNAL SIGTERM
CMD ["/opt/app/start-server.sh"]