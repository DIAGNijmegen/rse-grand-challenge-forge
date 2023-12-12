FROM --platform=linux/amd64 docker.io/library/python:3.11-slim

# Ensures that Python output to stdout/stderr is not buffered: prevents missing information when terminating
ENV PYTHONUNBUFFERED 1

RUN adduser --system --group user
USER user

WORKDIR /tmp

COPY --chown=user:user ground_truth /tmp/ground_truth

COPY --chown=user:user evaluate.py /tmp

ENTRYPOINT ["python", "evaluate.py"]
