# Hanalon

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/34ef29ce098648089ecae0f460917353)](https://www.codacy.com/gh/sakura-no-hana/hanalon/dashboard)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![made-with-python](https://img.shields.io/badge/Python-3.9&#8201;|&#8201;3.10-blue.svg)](https://www.python.org/)
[![Discord](https://img.shields.io/discord/715607808028049459.svg?label=&logo=discord&logoColor=ffffff&color=7389D8&labelColor=6A7EC2)](https://discord.gg/wKqGrKN)

Hanalon is an RPG Discord bot.

## Requirements

### Convenience

- bash
  - If you don't have bash, chances are that you're not on \*nix. On Windows 10, this can be remedied with [WSL](https://docs.microsoft.com/en-us/windows/wsl/install-win10). Unfortunately, for other operating systems, you may need to install a VM. Of course, it is still possible to run the bot without bash.

- [Perl](https://www.perl.org/get.html)
  - Similar to above, chances are, you're on a Windows machine. The perl script actually relies on bash, so it would be wise to get [WSL](https://docs.microsoft.com/en-us/windows/wsl/install-win10).

### Docker w/ Kubernetes

- [Kubectl](https://kubernetes.io/docs/tasks/tools/)
  - If you don't have much prior experience with Kubernetes, and aren't using this bot in production, I'd recommend using [minikube](https://minikube.sigs.k8s.io/docs/start/).

- [Docker](https://docs.docker.com/engine/install/#server)

### Docker

- [Docker](https://docs.docker.com/engine/install/#server)

### Python

- [Python 3.9+](https://www.python.org/downloads/)

## Usage

There are a few steps to use this Discord bot locally.

### Running

- Modify the `config.yaml` file. `token` is your bot token, `mongo` is your MongoDB connection URI, `guild` is the guild ID you plan on testing with, `devs` is a list of the developers' user IDs.

- `cd` into the parent directory of `src/`. This directory should look something like this:

  ```txt
  hanalon
  ├── Dockerfile
  ├── config.yaml
  ├── pyproject.toml
  ├── requirements.txt
  ├── scripts
  ⋮   └── hanalon.pl
  └── src
      ├── __main__.py
      ├── cogs
      │   ⋮
      │
      └── utils
          ⋮
  ```

- Run the bot

  - Docker w/ Kubernetes:
    - Through perl:  
      `perl scripts/hanalon.pl bot run k8s`

    - Through bash:  
      `kubectl create namespace hanalon`  
      `kubectl delete -f k8s.yaml --namespace=hanalon`  
      `kubectl delete secret hanalon-secret --namespace=hanalon`  
      `kubectl create secret generic hanalon-secret --namespace=hanalon --from-literal=config=$(base64 -in config.yaml)`  
      `kubectl apply -f k8s.yaml --namespace=hanalon`

  - Docker:
    - Through perl:  
      `perl scripts/hanalon.pl bot run docker`

    - Through bash:  
      `docker build -t hanalon/bot`  
      `docker stop hanalon-bot`  
      `docker run -d --rm --name hanalon-bot -e config=$(base64 -in config.yaml) hanalon-bot`  

  - Python:
    - Through perl:  
      `perl scripts/hanalon.pl bot run py -r=poetry`

    - Through bash:  
      `curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 -`  
      `poetry update`  
      `poetry install`  
      `nohup python3 src/__main__.py >/dev/null &`

Keep in mind that all of these processes need to be explicitly killed with `perl scripts/hanalon.pl bot kill`.

### Killing

You can kill the bot with perl:  
`perl scripts/hanalon.pl bot kill`

Or with bash, depending on how your bot was started:

- Kubernetes + Docker:  
  `kubectl delete -n hanalon statefulset hanalon-bot 2>&1`

- Docker:  
  `docker stop hanalon-bot`  
  `docker rm hanalon-bot`

- Python:  
  `pkill hanalon-bot`

## Contributing

Pull requests are always welcome. Please open an issue so that other contributors may fix an issue if you are unable to fix it yourself. For feature requests and the like, please open issues.

Keep in mind that even as a side-project, we have standards here. Thus, we've set up a `.pre-commit-config.yaml` for your use. We currently only run a check with black, but the pre-commit hook makes sure that your code has sorted imports, is black compliant, and that your `requirements.txt` matches your `poetry.lock`.

Dependencies are managed by Poetry, which uses `pyproject.toml`. Do not manually edit the `requirements.txt`; either let pre-commit do it for you, or run `poetry export -o requirements.txt --without-hashes`.

### Venv

It is highly recommended that you use a venv while developing. This makes it so inter-project dependency versions do not cause conflicts. You can create a venv with `python3 -m venv .venv`. You can then activate that venv with `source .venv/bin/activate`.

### Testing

Tests are located in the `tests` directory and use pytest. Either use the perl script provided (`perl scripts/hanalon.pl bot test --cov`) or manually run them (`pip3 install pytest ; pytest -v`). There is no required code coverage, but writing tests is simply good practice; do it if you can, but it's not a big deal if you can't.
