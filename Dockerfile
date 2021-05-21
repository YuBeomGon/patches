FROM doaihub/doai-openslide:1.0

WORKDIR /app

COPY . /app

# env setting
ENV LANG C.UTF-8
ENV PYTHONUNBUFFERED=0

## activate virtualenv
#RUN python3.6 -m venv papsmear
#RUN papsmear/bin/pip install --upgrade pip

# package install
RUN poetry config virtualenvs.create false
RUN poetry install

# start save-path app
CMD ["python3", "main.py"]
