FROM python:3.10-bullseye

ARG COMMIT=""
LABEL commit=${COMMIT}

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
ENV COMMIT_SHA=${COMMIT}

CMD [ "python", "-m", "sondehub_aprs_gw" ]