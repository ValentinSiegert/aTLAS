# <img src="/logos/atlas_orange.svg" alt="aTLAS orange" width="5%"> aTLAS

This is the repository of aTLAS, a Trust Laboratory for Multi-Agent Systems.

Latest online prototype: [https://vsr.informatik.tu-chemnitz.de/projects/2020/atlas/demo/](https://vsr.informatik.tu-chemnitz.de/projects/2020/atlas/demo/)

aTLAS project page: [https://vsr.informatik.tu-chemnitz.de/projects/2020/atlas/](https://vsr.informatik.tu-chemnitz.de/projects/2020/atlas/)

`djtrustlab` is the main Django project with settings.py, while `trustlab` is the Django app. The git submodule `trustlab_host` is the host library to start a supervisor on a host.

## Information
1. Python 3.7

2. Django v2

3. Local Redis

4. Pipenv or Python virtual environment

## Setup
1. Install Redis https://redis.io/topics/quickstart

2. Clone Git Repository, including all submodules.

3. Setup pipenv in project root:
    ```bash
    pipenv install
    ```
   **OR** install all requirements in your virtual environment for this project with:
   ```bash
    pip install -r requirements.pip --exists-action w
    ```
        
4. Modify ``Additional Options`` of your django configuration with (for no auto-reload after editing scenario files):
    ```bash
    --noreload
    ```

5. Install also at least one supervisor. (https://github.com/N0omB/aTLAS_host)

   
## Run

1. Run local Redis server

2. Run aTLAS:
    ```bash
    python3 manage.py runserver 8000 --noreload
    ```

3. Run at least on supervisor with the included submodule and connect it to aTLAS. (https://github.com/N0omB/aTLAS_host)


## How To Scenario

- Currently scenario configurations can be placed in ``trustlab/lab/scenarios``.

- Every scenario configuration file has to end with ``_scenario.py``.

- All scenario parameters require to be the upperCase version of the respective Scenario.\_\_init\_\_ arguments

- Possible scenario arguments derive from Scenario.\_\_init\_\_ arguments list, where parameters without default value are mandatory for scenario configuration file as well


## Links To Know

* aTLAS Project page \
https://vsr.informatik.tu-chemnitz.de/projects/2020/atlas/

* Latest online prototype \
https://vsr.informatik.tu-chemnitz.de/projects/2020/atlas/demo/

* Host Library Repository and Submodule at `trustlab_host` \
https://github.com/N0omB/aTLAS_host

<!-- Identifiers, in alphabetical order -->
[atlas-logo-orange]: /logos/atlas_orange.svg


