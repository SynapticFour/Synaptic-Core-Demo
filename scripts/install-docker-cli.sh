#!/usr/bin/env bash
# Install a checksummed static docker CLI for TES/WES (host docker.sock).
# Args: none. Uses TARGETARCH (buildx) or uname -m.
set -euo pipefail
VERSION="${DOCKER_CLI_VERSION:-27.5.1}"
ARCH_RAW="${TARGETARCH:-}"
if [[ -z "${ARCH_RAW}" ]]; then
  case "$(uname -m)" in
    x86_64|amd64) ARCH_RAW=amd64 ;;
    aarch64|arm64) ARCH_RAW=arm64 ;;
    *) echo "unsupported arch $(uname -m)" >&2; exit 1 ;;
  esac
fi
case "${ARCH_RAW}" in
  amd64)
    DOCKER_ARCH=x86_64
    SUM="${DOCKER_CLI_SHA256_AMD64:-4f798b3ee1e0140eab5bf30b0edc4e84f4cdb53255a429dc3bbae9524845d640}"
    ;;
  arm64)
    DOCKER_ARCH=aarch64
    SUM="${DOCKER_CLI_SHA256_ARM64:-e6b53725a73763ab3f988c73f8772eaed429754c1a579db5ff11f21990fd1817}"
    ;;
  *)
    echo "unsupported TARGETARCH=${ARCH_RAW}" >&2
    exit 1
    ;;
esac
URL="https://download.docker.com/linux/static/stable/${DOCKER_ARCH}/docker-${VERSION}.tgz"
curl -fsSL "${URL}" -o /tmp/docker.tgz
echo "${SUM}  /tmp/docker.tgz" | sha256sum -c -
tar -xz -C /tmp -f /tmp/docker.tgz
mv /tmp/docker/docker /usr/local/bin/docker
chmod +x /usr/local/bin/docker
rm -rf /tmp/docker /tmp/docker.tgz
