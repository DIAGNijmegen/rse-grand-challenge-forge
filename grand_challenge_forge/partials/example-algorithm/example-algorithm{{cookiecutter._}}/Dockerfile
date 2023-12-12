FROM --platform=linux/amd64 pytorch/pytorch
# Use a 'large' base container to show-case how to load pytorch and use the GPU (when enabled)

# Ensures that Python output to stdout/stderr is not buffered: prevents missing information when terminating
ENV PYTHONUNBUFFERED 1

RUN adduser --system --group user
USER user

WORKDIR /tmp

COPY --chown=user:user requirements.txt /tmp
COPY --chown=user:user resources /tmp/resources

RUN python -m pip install \
    --no-color \
    --requirement /tmp/requirements.txt

COPY --chown=user:user inference.py /tmp

ENTRYPOINT ["python", "inference.py"]
