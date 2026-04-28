# PMIx ReFrame Test Suite

A [ReFrame](https://reframe-hpc.readthedocs.io/en/stable/)-based testing framework for the **PMIx (Process Management Interface for Exascale)** library and runtime environment. This test suite automatically builds all dependencies from source and validates the PMIx stack through a series of functional tests.

## Overview

**What does this do?**

This test suite:
- Automatically downloads and builds three core components from source: `libevent`, `PMIx`, and `PRRTE`
- Ensures all components are built with compatible versions and linked correctly
- Validates the complete PMIx stack by running functional tests


## Project Structure

### File Organization

| File | Purpose |
|------|---------|
| `libevent_build_class.py` | Download and build the `libevent` library (base dependency) |
| `pmix_build_class.py` | Download and build `PMIx` (linked against `libevent`) |
| `prrte_build_class.py` | Download and build `PRRTE` (linked against `libevent` and `PMIx`) |
| `build_pmix_test.py` | Build test binaries (`hello_world`, `cycle`, `prun-wrapper`) |
| `run_pmix_test.py` | Main ReFrame test file - run all tests |
| `sysconfig.yaml` | ReFrame system configuration for your HPC cluster |
| `setup_env.sh` | Optional environment setup script |

### Build Dependency 

The test suite follows a strict build order to ensure all dependencies are satisfied:

```
libevent (base library)
    ↓
PMIx (depends on libevent)
    ↓
PRRTE (depends on both libevent and PMIx)
    ↓
PMIx Tests (hello_world, cycle, prun-wrapper)
```

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/NiccoloTosato/pmix-reframe-suite.git
   cd pmix-reframe-suite
   ```

2. **Create and activate a Python virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install ReFrame:**
   ```bash
   pip install reframe-hpc
   ```

4. **Configure your system** (edit `sysconfig.yaml`):
   Update the system name, partition, and access credentials to match your HPC cluster.

## Running the Tests

### Quick Start

Run all tests with default versions:
```bash
source setup_env.sh
reframe -C ./sysconfig.yaml -c run_pmix_test.py --system=odo:batch -r
```

### With Custom Component Versions

Specify different versions for any component:
```bash
reframe -C ./sysconfig.yaml -c run_pmix_test.py \
  --system=odo:batch \
  -S fetch_pmix.version="6.1.0" \
  -S fetch_prrte.version="4.1.0" \
  -S fetch_libevent.version="2.1.12" \
  -r
```

### Environment Variables

The `setup_env.sh` script sets useful ReFrame environment variables:
- `RFM_KEEP_STAGE_FILES=1`: Preserves build artifacts for debugging
- `RFM_CONFIG_FILES`: Points to the system configuration
- `RFM_PREFIX`: Output directory for test results

You can also set these manually before running tests.

## Execution Flow

The test suite executes in the following phases:

### Phase 1: Download
- `fetch_libevent` downloads `libevent` source
- `fetch_pmix` downloads `PMIx` source
- `fetch_prrte` downloads `PRRTE` source
- `fetch_pmixtest` clones the `pmix-tests` repository

### Phase 2: Build
- `build_libevent` compiles `libevent` and installs to staging directory
- `build_pmix` compiles `PMIx`, explicitly linking against the built `libevent`
- `build_prrte` compiles `PRRTE`, linking against both built `libevent` and `PMIx`

### Phase 3: Test Preparation
- `build_hello_world`, `build_cycle`, `build_prun_wrapper` build test binaries
- Environment variables (`PATH`, `LD_LIBRARY_PATH`) are configured to use the locally built libraries

### Phase 4: Test Execution
- Each test runs in the configured environment
- Tests validate the PMIx stack functionality

