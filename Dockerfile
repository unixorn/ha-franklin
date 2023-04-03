FROM python:3.10-slim-bullseye
LABEL maintainer="Joe Block <jpb@unixorn.net>"
LABEL description="ha monitoring tool for cupsd"
LABEL version=${application_version}

# Install Packages (basic tools, cups, fonts, HP drivers, laundry list drivers)
RUN apt-get update \
&& apt-get install -y --no-install-recommends apt-utils ca-certificates \
&& update-ca-certificates \
&& apt autoremove -y \
&& apt-get install -y --no-install-recommends \
  cups-bsd \
  cups-client \
&& apt-get clean \
&& rm -rf /var/lib/apt/lists/* /tmp/*

RUN mkdir -p /app

# Speed up dev image bakes
COPY requirements.txt /app
RUN pip install --upgrade --no-cache-dir pip \
  && pip install --no-cache-dir -r /app/requirements.txt \
  && rm -fr /tmp/*

COPY dist/*.whl /app
RUN pip install --no-cache-dir --disable-pip-version-check /app/*.whl \
  && rm -fr /tmp/*

# Default shell
CMD ["/bin/bash",]
