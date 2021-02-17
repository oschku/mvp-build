FROM python:3.8-slim AS compile-image

RUN apt-get update
RUN apt-get install -y --no-install-recommends build-essential gcc

# We copy just the requirements.txt first to leverage Docker cache
COPY requirements.txt .
RUN pip install --user -r requirements.txt
RUN pip3 install --user sqlalchemy-datatables==2.0.1




FROM python:3.8-slim AS build-image
COPY --from=compile-image /root/.local /root/.local

COPY . /app
ADD . /

# Make sure scripts in .local are usable:
ENV PATH=/root/.local/bin:$PATH
WORKDIR /app
ENTRYPOINT [ "python" ]
CMD [ "launch.py", "--host", "0.0.0.0"]
EXPOSE 5000