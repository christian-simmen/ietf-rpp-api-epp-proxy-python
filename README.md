## Installation

Create and activate python virtual environment
```
python -m venv .venv
. .venv/bin/activate
```

Install modules
```
pip install -r requirements.txt 
```

For development, install `requirements-dev.txt` instead, which adds the tools of the checks.

## Running
```
cd src
uvicorn main:app
```

The proxy reads `config.yaml` from the working directory (`src/config.yaml` is a link to the one in the repository
root), or the file `RPP_CONFIG_FILE` names. An untracked `<name>.local.yaml` next to that file replaces the top-level
keys it has, for one machine's settings.

The proxy speaks EPP to the registry by default. `rpp_backend: rri` in the config file makes it speak DENIC RRI 5.0
(XML) instead, with the `rpp_rri_*` settings; [config.rri-mtest.yaml](config.rri-mtest.yaml) is the one for DENIC's
test environment. One deployment speaks one protocol, and the RPP API is the same for both. What RRI cannot hold or
do answers 501: host objects, client statuses, renew, transfers, contact deletion, a readable authInfo. See
[docs/rri/](docs/rri/) for the mapping.

Swagger UI shall be available at http://127.0.0.1:8000/ui/

The username and password of HTTP Basic are the EPP login (`clID`/`pw`), and every request needs an `RPP-Cltrid`
header with a new value.

## Local EPP server

[EPP-server-docker](https://github.com/pawel-kow/EPP-server-docker) runs an EPP test registry (XPanel) in docker
compose. Its README has the details; in short:

```
git clone https://github.com/pawel-kow/EPP-server-docker.git
cd EPP-server-docker
git submodule update --init                  # the submodule URL uses SSH, so this needs a GitHub SSH key
docker compose -p epptest --profile setup up # once: provisions the database
docker compose -p epptest --profile setup down
docker compose -p epptest --profile run up -d
```

Use the project name `epptest` with every compose command: [config.yaml](config.yaml) reaches the server as
`epp-server` on TLS port 743, a name that resolves only on the compose network `epptest_epp_net`. From the docker
host the server is on `localhost:7043` (TLS) instead. Its certificate is self-signed, so `config.yaml` sets
`rpp_epp_tls_insecure_skip_verify`; never set it against a real registry.

It provisions two registrars, `foo`/`bar` and `baz`/`qux`, with the contact id prefixes `FO-` and `BZ-`, and
registers under the TLD `example`. It refuses a reused `clTRID`, also across sessions.

To run the proxy against it:

- **In the devcontainer:** join the devcontainer to the network (again after each rebuild), then run the proxy as in
  [Running](#running):
  ```
  docker network connect epptest_epp_net $(cat /etc/hostname)
  ```
- **On the docker host:** put the host's address of the server in an untracked `config.local.yaml` in the repository
  root, and point the proxy at the root `config.yaml`, so the local file next to it applies:
  ```
  printf 'rpp_epp_host: localhost\nrpp_epp_port: 7043\n' > config.local.yaml
  cd src && RPP_CONFIG_FILE=../config.yaml uvicorn main:app
  ```
- **In docker:** see [Running docker](#running-docker).

A quick check, a domain check as `foo`:
```
curl -I -u foo:bar -H 'Accept: application/rpp+json' -H "RPP-Cltrid: $(uuidgen)" \
  http://127.0.0.1:8000/domainNames/my-test.example/availability
```

For the integration tests, copy [.env.example](.env.example) to `.env` and fill in the `TEST_EPP_*` variables with
these registrars; see [docs/agents/testing.project.md](docs/agents/testing.project.md#backend).

## Building docker
```
docker build . -f ./.docker/Dockerfile -t pawelk/rpp_server_epp_proxy
```

The image holds [config.yaml](config.yaml) as it is at build time.

## Running docker
```
docker run --rm -p 8000:8091 pawelk/rpp_server_epp_proxy
```

The proxy listens on 8091 in the container, so Swagger UI is at http://127.0.0.1:8000/ui/.

Against the [local EPP server](#local-epp-server), join the container to its network, where the built-in
`config.yaml` finds it:
```
docker run --rm -p 8000:8091 --network epptest_epp_net pawelk/rpp_server_epp_proxy
```

With a config of your own, mount it and name it in `RPP_CONFIG_FILE`:
```
docker run --rm -p 8000:8091 -v "$PWD/my-config.yaml:/config/config.yaml:ro" \
  -e RPP_CONFIG_FILE=/config/config.yaml pawelk/rpp_server_epp_proxy
```
