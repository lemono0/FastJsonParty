FROM centos:centos7.9.2009


RUN yum install java-1.8.0-openjdk-1.8.0.362.b08-1.el7_9.x86_64 -y

RUN  mkdir /var/app && \
     mkdir /usr/lib/jvm/java-1.8.0-openjdk-1.8.0.362.b08-1.el7_9.x86_64/jre/classes

COPY app.jar /var/app/

COPY flag /f149

WORKDIR /root

USER root

#EXPOSE 80

CMD ["java","-jar","/var/app/app.jar"]
