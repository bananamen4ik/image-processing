FROM ubuntu:26.04

ENV PATH="/root/.local/bin:$PATH"

RUN <<EOT
apt update
apt upgrade -y
apt install -y curl
curl -LsSf https://astral.sh/uv/0.13.6/install.sh | env UV_NO_MODIFY_PATH=1 sh
EOT

WORKDIR /opt/src

COPY pyproject.toml uv.lock .python-version ./

WORKDIR image-processing

ENTRYPOINT ["uv", "run", "--locked", "--all-extras", "--dev", "celery", "-A", "image_processing", "worker", "-l", "INFO"]