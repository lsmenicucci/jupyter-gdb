# Start from the Intel oneAPI HPC Kit base image
FROM intel/fortran-essentials:latest

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install gdb
RUN apt-get update && apt-get install -y gdb

WORKDIR /workspace

RUN uv venv /.venv
ENV VIRTUAL_ENV="/.venv"

RUN uv pip install \
    jupyterlab numpy pygdbmi \
    matplotlib


# Create env and install dependencies
#RUN uv venv .venv 
#ENV PATH="/workspace/.venv/bin:$PATH"

# Run jupyter lab and uv
CMD ["uv", "run", \
        "jupyter", "lab", "--allow-root", "--ip=0.0.0.0"]
