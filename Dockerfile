# Build Synaptic-Core from a pinned GitHub ref with Choice A adapters.
# SPDX-License-Identifier: Apache-2.0
# make up-pinned clones a PRIVATE repo (SynapticFour/Synaptic-Core).
# Outsiders: use make up-sibling with a local checkout.

ARG SYNAPTIC_CORE_REF=ffbc955cb611bf9bb2ddf7dafe84ab96a0213a79
ARG RUST_IMAGE=rust:1.91.1-bookworm
ARG TARGETARCH

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
ARG TARGETARCH
ARG DOCKER_CLI_VERSION=27.5.1
ARG DOCKER_CLI_SHA256_AMD64=4f798b3ee1e0140eab5bf30b0edc4e84f4cdb53255a429dc3bbae9524845d640
ARG DOCKER_CLI_SHA256_ARM64=e6b53725a73763ab3f988c73f8772eaed429754c1a579db5ff11f21990fd1817
# Checksummed docker CLI for TES/WES via mounted /var/run/docker.sock (localhost demo only).
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates curl \
    && arch="${TARGETARCH:-amd64}" \
    && case "${arch}" in \
         amd64) darch=x86_64; sum="${DOCKER_CLI_SHA256_AMD64}" ;; \
         arm64) darch=aarch64; sum="${DOCKER_CLI_SHA256_ARM64}" ;; \
         *) echo "unsupported TARGETARCH=${arch}" >&2; exit 1 ;; \
       esac \
    && curl -fsSL "https://download.docker.com/linux/static/stable/${darch}/docker-${DOCKER_CLI_VERSION}.tgz" -o /tmp/docker.tgz \
    && echo "${sum}  /tmp/docker.tgz" | sha256sum -c - \
    && tar -xz -C /tmp -f /tmp/docker.tgz \
    && mv /tmp/docker/docker /usr/local/bin/docker \
    && rm -rf /tmp/docker /tmp/docker.tgz \
    && apt-get purge -y curl && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*
COPY --from=builder /src/synaptic-core/target/release/sc-server /usr/local/bin/sc-server
ENV SC_SERVER_BIND_ADDR=0.0.0.0:8080
EXPOSE 8080
ENTRYPOINT ["/usr/local/bin/sc-server"]
