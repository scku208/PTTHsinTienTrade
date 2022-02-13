FROM continuumio/miniconda3
LABEL maintainer="ku88@ku88.xyz" \
      ku88.release-date="2022-02-13" \
      ku88.version="0.1.1"

COPY ./environment.yaml .

EXPOSE 8080/tcp

RUN conda update -n base -c defaults -y conda \
    && conda env create --file /environment.yaml

CMD ["conda", "run", "--no-capture-output", "-n", "app", "/bin/bash", "-c", "cd /app&&uwsgi --ini app.ini --manage-script-name"]
