# base image
# a little overkill but need it to install dot cli for dtreeviz
# FROM ubuntu:18.04
# # ubuntu installing - python, pip, graphviz
# RUN apt-get update &&\
#     apt-get install python3.7 -y &&\
#     apt-get install python3-pip
FROM python:3.7
# exposing default port for streamlit
EXPOSE 8501
# making directory of app
# WORKDIR /wdsqa
# copy over requirements
COPY requirements.txt ./requirements.txt
# install pip then packages
RUN pip3 install -r requirements.txt
# copying all files over
COPY . .
# cmd to launch app when container is run
CMD streamlit run app_wds.py
# streamlit-specific commands for config
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
RUN mkdir -p /root/.streamlit
RUN bash -c 'echo -e "\
[server]\n\
enableCORS = false\n\
" > /root/.streamlit/config.toml'