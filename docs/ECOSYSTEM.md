# Synaptic Core stack (you are in Synaptic-Core-Demo)

Four product repos implement a domain-agnostic scientific compute fabric. This demo sits **beside** them and exercises a live Core with Choice A adapters.

| Repository | Role | License |
|------------|------|---------|
| [sc-specs](https://github.com/SynapticFour/sc-specs) | OpenAPI / AsyncAPI | CC0-1.0 |
| [Synaptic-Core](https://github.com/SynapticFour/Synaptic-Core) | Reference Rust server | BUSL-1.1 |
| [sc-transport](https://github.com/SynapticFour/sc-transport) | Telemetry + SPARQ | BUSL-1.1 |
| [Synaptic-Core-Test](https://github.com/SynapticFour/Synaptic-Core-Test) | Conformance (`synaptictest` / `sctest`) | Apache-2.0 |
| **Synaptic-Core-Demo** (this repo) | Fail-closed Choice A API smokes | Apache-2.0 |

Related genomic deep demo: [Ferrum-GA4GH-Demo](https://github.com/SynapticFour/Ferrum-GA4GH-Demo). Clinical demo: [Solum-Demo](https://github.com/SynapticFour/Solum-Demo).

## Lifecycle

```bash
cd Synaptic-Core-Demo
make up            # sibling ../Synaptic-Core
make demo-all      # COMPLETE or fail
make down
```
