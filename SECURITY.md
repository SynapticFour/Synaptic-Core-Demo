# Security Policy

## Reporting a Vulnerability

Please do **not** open public GitHub issues for security vulnerabilities.

Report vulnerabilities privately to **contact@synapticfour.com** with:
- affected repository and version/commit
- reproduction steps or proof-of-concept
- impact assessment

We will acknowledge receipt as quickly as possible, triage severity, and coordinate a responsible disclosure timeline.

## Scope and Guarantees

This project is a local demo harness. The default compose file binds the API to 127.0.0.1 and mounts the host Docker socket so TES/WES can reach COMPLETE. Do not publish that socket or the API on a network. No absolute security guarantee is provided.
