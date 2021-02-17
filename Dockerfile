FROM python:3.8 AS builder

# We copy just the requirements.txt first to leverage Docker cache
COPY requirements.txt /app/requirements.txt

RUN pip install --user -r requirements.txt
RUN pip3 install sqlalchemy-datatables==2.0.1


FROM python:3.8-slim
WORKDIR /app

# copy only the dependencies installation from the 1st stage image
COPY --from=builder /root/.local/bin /root/.local
COPY ./src .

# update PATH environment variable
ENV PATH=/root/.local:$PATH
COPY . /app
ADD . /

ENTRYPOINT [ "python" ]
CMD [ "launch.py", "--host", "0.0.0.0"]
EXPOSE 5000