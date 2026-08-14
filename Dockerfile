# Build Synaptic-Core from a pinned GitHub ref with Choice A adapters.
# SPDX-License-Identifier: Apache-2.0

ARG SYNAPTIC_CORE_REF=5f375d96367c8fe422cc975c13ea7e3ede8fb34e
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
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*
COPY --from=builder /src/synaptic-core/target/release/sc-server /usr/local/bin/sc-server
ENV SC_SERVER_BIND_ADDR=0.0.0.0:8080
EXPOSE 8080
ENTRYPOINT ["/usr/local/bin/sc-server"]
