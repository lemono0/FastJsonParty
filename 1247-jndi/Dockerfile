From openjdk:8u121-jdk-alpine

RUN mkdir /var/app

COPY 1247-jndi.jar /var/app/
COPY flag /flag

WORKDIR /var/app

EXPOSE 80

USER ctf

CMD [ "java","-jar","/var/app/1247-jndi.jar" ]
