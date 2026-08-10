# AGENTS.md

## Repository Overview

`ida-auth-sdk` is a Python client library ("MOSIP Authentication SDK") that wraps
calls to the MOSIP IDA (ID Authentication) service. It builds, encrypts, signs, and
sends `auth` and `kyc` requests, and decrypts the responses returned by the server.
It is a single Python package — there are no independent sub-modules or other
language bindings in this repo, so this one root file is the complete guide.

The package exposes:

- `MOSIPAuthenticator` (from `mosip_auth_sdk`) — the main client class, with
  `auth(...)` and `kyc(...)` methods.
- `mosip_auth_sdk.models` — Pydantic models (`DemographicsModel`, `IdentityInfo`,
  `BiometricModel`, etc.) used to build request payloads.

Reference API docs for the underlying MOSIP service endpoints:

- [kyc-auth-controller](https://mosip.github.io/documentation/1.2.0/authentication-service.html#tag/kyc-auth-controller)
- [auth-controller](https://mosip.github.io/documentation/1.2.0/authentication-service.html#operation/authenticateIndividual)

## Technology Stack

- **Language**: Python, `^3.10` (per `pyproject.toml`; README notes it was tested
  on 3.10.7).
- **Packaging**: [Poetry](https://python-poetry.org/) (`pyproject.toml`,
  `poetry.lock`), build backend `poetry.core.masonry.api`.
- **Runtime dependencies** (from `pyproject.toml`): `pydantic ^2.9.2`,
  `requests ^2.32.3`, `cryptography ^43.0.3`, `jwcrypto ^1.5.6`.
- **Dev-only dependency**: `dynaconf ^3.2.6` (used to load `.toml` config files
  for the examples and tests).
- No `.github/workflows` directory exists in this repo — there is currently no
  CI pipeline defined for this project. Do not claim CI runs any check.

## Build & Test Commands

Install Poetry, then install dependencies:

```bash
python3 -m pip install poetry
python3 -m poetry install
```

Or, without Poetry:

```bash
python3 -m pip install -r requirements.txt
```

Build a distributable package:

```bash
python3 -m poetry build
```

Publish (maintainers only):

```bash
python3 -m poetry publish
```

Run the example script (requires a valid `config.toml`, see Configuration below):

```bash
python examples/main.py
```

Note: `examples/main.py` is referenced by the README, but the `examples/`
directory as it currently exists on `develop` contains `demo_auth.py`,
`demo_kyc.py`, `otp_generate.py`, `otp_verify.py`, and `config.toml` — no
`main.py`. Check the actual file names in `examples/` before telling a user to
run a specific script; use `demo_auth.py` or `demo_kyc.py` as the runnable
entry points instead if `main.py` is absent.

Tests live in `tests/test_authenticator.py`. As of this writing that file is
empty (no test cases are implemented yet), and no `pytest.ini`/`tox.ini` is
present. If you add tests, use `pytest` and add real fixtures/config rather
than assuming a runner is already wired up.

## Configuration

Configuration is TOML-based and loaded with `dynaconf`. Two example files exist:

- `mosip_auth_sdk/_authenticator/authenticator-config.toml` — a blank template
  showing every expected key (empty strings for secrets/paths).
- `examples/config.toml` — a filled-in **sample** used by the example scripts,
  pointing at a staging environment (`ida_auth_env = 'Staging'`,
  `ida_auth_domain_uri = 'https://api-internal.env.mosip.net'`) with a sample
  partner API key/MISP license key and a sample P12 keystore password
  (`Password@123`). Treat every value in `examples/config.toml` as a
  placeholder for local experimentation only — never reuse these values, and
  never commit real partner credentials, API keys, or keystore passwords in
  their place.

Key config sections (see `authenticator-config.toml` for the authoritative list):

- `[mosip_auth]` — partner API key, MISP license key, partner ID, request IDs.
- `[mosip_auth_server]` — the IDA base URL and domain URI.
- `[crypto_encrypt]` — `encrypt_cert_path` (public cert used to encrypt the
  outgoing auth request) and `decrypt_p12_file_path` /
  `decrypt_p12_file_password` (PKCS#12 keystore used to decrypt the response).
- `[crypto_signature]` — `sign_p12_file_path` / `sign_p12_file_password`
  (PKCS#12 keystore used to JWS-sign the request) and the signing `algorithm`
  (`RS256`).
- `[logging]` — log file path, format, and level.

Certificate/keystore handling notes (verified against
`mosip_auth_sdk/_authenticator/utils/cryptoutil.py`):

- `.gitignore` excludes a `certs` directory ("Certificates stored in the sdk.
  Certificates can also be provided externally") and `.dockerignore` also
  excludes `certs`. Keep real certificates and `.p12` keystores out of version
  control — put them in a local, gitignored `certs/`-style path and reference
  that path from your `config.toml`, never hardcode secrets in code.
- `CryptoUtility` loads the encryption certificate as PEM first, falling back
  to DER if PEM parsing fails (`_get_certificate_obj`). Both formats are
  accepted for `encrypt_cert_path`.
- Both the decrypt and sign private keys are loaded from PKCS#12 (`.p12`)
  files via `pkcs12.load_key_and_certificates`, each with its own password
  field in the TOML config. These can point at the same or different `.p12`
  files depending on deployment.

## Project Structure Notes

```text
ida-auth-sdk/
├── mosip_auth_sdk/                  # the installable package
│   ├── __init__.py                  # exports MOSIPAuthenticator
│   ├── _authenticator/
│   │   ├── authenticator.py         # MOSIPAuthenticator: auth()/kyc() and request building
│   │   ├── auth_models.py           # Pydantic request models
│   │   ├── authenticator-config.toml# blank config template (documents every key)
│   │   ├── exceptions/              # AuthenticatorCryptoException, Errors enum, etc.
│   │   └── utils/
│   │       ├── cryptoutil.py        # CryptoUtility: encrypt/decrypt/sign auth data
│   │       └── restutil.py          # HTTP request helpers (requests-based)
│   └── models/
│       └── __init__.py              # re-exports DemographicsModel, BiometricModel, etc.
├── examples/                        # runnable sample scripts + sample config.toml
├── tests/
│   └── test_authenticator.py        # currently empty — no test cases implemented
├── pyproject.toml / poetry.lock     # Poetry package metadata and lock file
├── requirements.txt                 # pip-installable pinned dependency list (with hashes)
└── README.md
```

The leading underscore on `_authenticator` marks it as a private implementation
package — the public surface is what `mosip_auth_sdk/__init__.py` and
`mosip_auth_sdk/models/__init__.py` re-export. Prefer importing from
`mosip_auth_sdk` and `mosip_auth_sdk.models` rather than reaching into
`_authenticator` directly, to match how `examples/demo_auth.py` and
`examples/demo_kyc.py` do it.

## Development Workflow

1. Install dependencies with Poetry (preferred) or `pip install -r
   requirements.txt` (see Build & Test Commands).
2. Copy `mosip_auth_sdk/_authenticator/authenticator-config.toml` (or
   `examples/config.toml`) to your own local, gitignored config file and fill
   in real values (partner API key, MISP license key, certificate paths,
   `.p12` keystore paths/passwords) for the environment you are targeting.
   Never commit the filled-in file.
3. Make code changes under `mosip_auth_sdk/`.
4. If you touch `mosip_auth_sdk/_authenticator/utils/cryptoutil.py` or
   `restutil.py`, be precise: these implement asymmetric (RSA-OAEP/SHA-256)
   and symmetric (AES-GCM) crypto plus JWS signing that must interoperate with
   the MOSIP IDA server's Java implementation. Do not change padding,
   algorithm, or encoding choices without checking against the IDA service's
   expectations (the code comments cross-reference MOSIP's `keymanager`
   `CryptoCore.java` for exact algorithm parity).
5. There is no populated automated test suite in this repo yet
   (`tests/test_authenticator.py` is empty) and no CI workflow. Manually
   exercise changes against a running MOSIP IDA environment using the
   `examples/` scripts, and add real `pytest` cases when you add behavior.
6. Update `README.md` and this file if you change the public API
   (`MOSIPAuthenticator.auth`/`.kyc` signatures, or the models under
   `mosip_auth_sdk/models`).

## Pull Request Guidelines

- Keep changes focused on the SDK's public contract described in `README.md`
  (`auth`, `kyc`, and the model classes) — avoid unrelated refactors in the
  same PR.
- Do not include any real certificates, `.p12` keystores, API keys, MISP
  license keys, or passwords in commits, examples, or test fixtures. Sample
  values in `examples/config.toml` are placeholders — do not replace them with
  real credentials even for a demo commit.
- Follow MOSIP's general contribution process referenced in the project
  README for the PR title/description conventions used across MOSIP repos.
- Since there is no CI in this repo, run `python3 -m poetry build` locally (or
  the pip-based install) to confirm the package still installs and imports
  cleanly before opening a PR.

## Repository-Specific Considerations

- This SDK signs and encrypts real biometric/demographic authentication
  requests. Treat any change to `cryptoutil.py`, `restutil.py`, or the request
  models as security-sensitive — get it reviewed carefully, and never log
  decrypted identity data or private key material (existing code logs
  operations, e.g. "Creating certificate Object...", but not secret values —
  keep it that way).
- The `partner_apikey`, `partner_misp_lk`, and `partner_id` values in
  `[mosip_auth]` identify the calling partner to IDA; they are credentials,
  not public identifiers — handle them with the same care as passwords.
- `ida_auth_env` in `[mosip_auth]` and the URLs in `[mosip_auth_server]`
  select the target MOSIP environment (e.g. `Staging`). Double check these
  before running any example against a real deployment.

## Agent rules

### Do

1. Verify file names and paths against the actual `develop` branch tree
   before referencing them (e.g. confirm whether `examples/main.py` exists
   before telling someone to run it).
2. Keep all real certificates, `.p12` keystores, API keys, and passwords out
   of git — use the gitignored `certs`-style local paths and your own local
   config file copies.
3. Treat `cryptoutil.py` and `restutil.py` changes as security-sensitive and
   cross-check algorithm/encoding choices against the MOSIP IDA service they
   talk to.
4. Update `README.md` and this `AGENTS.md` together when the public API
   (`MOSIPAuthenticator`, `mosip_auth_sdk.models`) changes.
5. Use Poetry (`pyproject.toml`/`poetry.lock`) as the source of truth for
   dependency versions; keep `requirements.txt` in sync if you change
   dependencies.

### Do not

1. Do not claim a CI pipeline validates changes — this repo has no
   `.github/workflows` at present.
2. Do not commit filled-in config files, sample or real, that contain
   API keys, MISP license keys, or `.p12` passwords.
3. Do not assume `tests/test_authenticator.py` has coverage — it is currently
   empty; do not describe this repo as test-covered.
4. Do not change cryptographic algorithm, padding, or key-format choices in
   `cryptoutil.py` without confirming compatibility with the MOSIP IDA
   server's expectations.
5. Do not invent commands, file paths, or config keys not present in this
   repository — verify against `pyproject.toml`, the `.toml` config files,
   and the actual source tree first.
