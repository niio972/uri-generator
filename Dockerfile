FROM tiangolo/uwsgi-nginx-flask:python3.7

LABEL maintainer="Jean-Eudes Hollebecq <jean-eudes.hollebecq@inrae.fr>"
COPY . /app
RUN chmod +rwx /app
ENV STATIC_INDEX 0
ENV LISTEN_PORT 5000
EXPOSE 5000
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT [ "python" ]
CMD ["app/main.py"]