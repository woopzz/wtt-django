FROM python:3.13

ARG USERNAME="peon"
ARG USER_UID=1000
ARG USER_GID=1000

ARG WORKDIR=/app

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME

WORKDIR $WORKDIR

COPY requirements.txt $WORKDIR
RUN pip install -r requirements.txt

RUN chown -R $USERNAME:$USERNAME $WORKDIR

EXPOSE 8000

USER $USERNAME
