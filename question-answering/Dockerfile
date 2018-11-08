FROM continuumio/miniconda3

ADD questionanswering /root/questionanswering
ADD requirements.txt /root/requirements.txt

RUN pip install -r /root/requirements.txt && \
    rm /root/requirements.txt

WORKDIR /root
ENTRYPOINT ["python", "-m", "questionanswering.server"]
