FROM --platform=linux/amd64 docker.io/library/python:3.11-slim

# Ensures that Python output to stdout/stderr is not buffered: prevents missing information when terminating
ENV PYTHONUNBUFFERED 1

RUN groupadd -r user && useradd -m --no-log-init -r -g user user
USER user

WORKDIR /tmp

COPY --chown=user:user requirements.txt /tmp
COPY --chown=user:user ground_truth /tmp/ground_truth

# You can add any Python dependencies to requirements.txt
RUN python -m pip install \
    --user \
    --no-cache-dir \
    --no-color \
    --requirement /tmp/requirements.txt

COPY --chown=user:user evaluate.py /tmp

ENTRYPOINT ["python", "evaluate.py"]
