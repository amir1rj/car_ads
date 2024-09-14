FROM python:3.10.13-bookworm
EXPOSE 8000
WORKDIR /source

COPY requirements.txt /source

RUN pip install -U pipD
RUN pip cache purge
RUN pip install -r requirements.txt
ENV DJANGO_SETTINGS_MODULE=car_ads.settings

COPY . /source
CMD ["python","manage.py", "runserver", "0.0.0.0:8000"]
