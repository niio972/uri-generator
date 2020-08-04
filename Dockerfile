FROM tiangolo/uwsgi-nginx-flask:python3.7

LABEL maintainer="Jean-Eudes Hollebecq <jean-eudes.hollebecq@inrae.fr>"
COPY . /app
ENV STATIC_URL /static
ENV STATIC_PATH /app/static
ENV STATIC_INDEX 0
ENV LISTEN_PORT 5000
EXPOSE 5000
WORKDIR /app
RUN pip install -r requirements.txt
ENV PYTHONPATH=/app
ENV UWSGI_CHEAPER 4
ENV UWSGI_PROCESSES 64
ENTRYPOINT [ "python" ]
CMD ["app.py"]