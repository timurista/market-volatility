FROM python:3.7
MAINTAINER timurista@ducker.hub

WORKDIR /usr/src/

COPY . .
# COPY src/handler.py .
# COPY src/fang_volatility_rank.py .
# COPY src/requirements.py .


# install the reqs
RUN python3 -m pip install --no-cache-dir -r requirements.txt

# get the cron job
RUN apt-get update && apt-get -y install cron

ENV FOO=foofoo

# Copy cron-job file to the cron.d directory
COPY cron-job /etc/cron.d/cron-job

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/cron-job

# Apply cron job
RUN crontab /etc/cron.d/cron-job

# Create the log file to be able to run tail
RUN touch /var/log/cron.log

ARG GITHUB_ACCESS_TOKEN=${GITHUB_ACCESS_TOKEN}

RUN echo "TOKEN"
RUN echo $GITHUB_ACCESS_TOKEN

# Run the command on container startup
CMD cron && tail -f /var/log/cron.log

# ENTRYPOINT [ "/usr/bin/python3" ]
# ENTRYPOINT [""]
ENTRYPOINT [ "python3","handler.py" ]