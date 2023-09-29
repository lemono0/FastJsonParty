From openjdk:8u131

RUN mkdir /var/app

COPY app.jar /var/app/
COPY flag /flag

WORKDIR /var/app

USER root

CMD [ "java","-jar","/var/app/app.jar" ]