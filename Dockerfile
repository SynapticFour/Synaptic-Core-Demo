# Build Synaptic-Core from a pinned GitHub ref with Choice A adapters.
# SPDX-License-Identifier: Apache-2.0

ARG SYNAPTIC_CORE_REF=ffbc955cb611bf9bb2ddf7dafe84ab96a0213a79
ARG RUST_IMAGE=rust:1.91.1-bookworm

FROM ${RUST_IMAGE} AS builder
ARG SYNAPTIC_CORE_REF
WORKDIR /src
RUN apt-get update && apt-get install -y --no-install-recommends git ca-certificates \
    && rm -rf /var/lib/apt/lists/*
RUN git clone --depth 1 https://github.com/SynapticFour/Synaptic-Core.git synaptic-core \
    && cd synaptic-core \
    && git fetch --depth 1 origin "${SYNAPTIC_CORE_REF}" \
    && git checkout "${SYNAPTIC_CORE_REF}"
WORKDIR /src/synaptic-core
RUN cargo build --release -p synaptic-core-server \
    --features adapter-ga4gh,adapter-stac,adapter-bids

FROM debian:bookworm-slim AS runtime
# docker CLI talks to the host daemon via mounted /var/run/docker.sock (TES/WES tasks).
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates curl \
    && curl -fsSL https://download.docker.com/linux/static/stable/x86_64/docker-27.5.1.tgz \
      | tar -xz -C /tmp \
    && mv /tmp/docker/docker /usr/local/bin/docker \
    && rm -rf /tmp/docker \
    && apt-get purge -y curl && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*
COPY --from=builder /src/synaptic-core/target/release/sc-server /usr/local/bin/sc-server
ENV SC_SERVER_BIND_ADDR=0.0.0.0:8080
EXPOSE 8080
ENTRYPOINT ["/usr/local/bin/sc-server"]
