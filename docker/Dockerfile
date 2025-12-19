# python:3.13-slim AS build
FROM debian:latest AS build

RUN apt update
RUN apt install -y python3-webview python3-venv
RUN python3 -m venv /venv
RUN apt install -y npm curl
RUN npm i -g n
RUN n latest
RUN apt install -y make
RUN apt install -y python3-dev
COPY ./custom-elements /app/custom-elements
WORKDIR /app/custom-elements
RUN npm i
WORKDIR /app
COPY ./build_requirements.txt /app/build_requirements.txt
RUN /venv/bin/pip install -r build_requirements.txt
COPY ./docker/components.mk /app/components.mk
COPY ./docker/packaging.mk /app/packaging.mk
COPY ./docker/wheel.mk /app/wheel.mk
COPY ./docker/Makefile /app/Makefile
COPY ./docker/cython-compile.list /app/cython-compile.list
RUN make prepare-all
COPY ./pyproject.toml /app/pyproject.toml
COPY ./README.md /app/README.md
COPY ./src /app/src
RUN make build-wheel
RUN make package
#RUN make package-python
#RUN make package-onefile



FROM scratch AS export
COPY --from=build /app/untext /untext
#COPY --from=build /app/untext-python /untext-python
#COPY --from=build /app/untext-onefile /untext-onefile
COPY --from=build /app/dist/untext-*.whl /dist/
COPY --from=build /app/dist/untext-*.tar.gz /dist/
