FROM ubuntu:18.04
ENV LC_ALL=en_US.UTF-8 TERM=xterm COLS=132 ROWS=43 DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y locales && locale-gen $LC_ALL && \
    apt-get install --no-install-recommends -y \
            python3-pip \
            python3-dev \
            openjdk-11-jdk \
            openjdk-11-jre \
            gcc \
            libc6-dev \
            curl \
	    git \
            && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Package versions are the latest as of when this script was last updated,
# unless otherwise noted.
RUN pip3 install setuptools \
    wheel==0.32.3

# Install the list of core requirements, e.g. sklearn, numpy, pandas, flask.
COPY dr_requirements.txt dr_requirements.txt
RUN pip3 install -r dr_requirements.txt --no-cache-dir && \
    rm -rf dr_requirements.txt

RUN pip3 install --upgrade git+https://github.com/autodeployai/pypmml.git

# Copy the drop-in environment code into the correct directory
# Code from the custom model tarball can overwrite the code here
COPY ./ /opt/code/
