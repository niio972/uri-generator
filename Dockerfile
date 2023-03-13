FROM tiangolo/uwsgi-nginx-flask:python3.7
LABEL maintainer="Jean-Eudes Hollebecq <jean-eudes.hollebecq@inrae.fr>"
RUN echo "lol"
RUN /usr/local/bin/python -m pip install --upgrade pip
COPY ./app /app
RUN chmod +rwx -R /app
ENV STATIC_INDEX 0
ENV LISTEN_PORT 3838
EXPOSE 3838
RUN pip install -r /app/requirements.txt
ENTRYPOINT [ "python" ]
CMD ["/app/main.py"]