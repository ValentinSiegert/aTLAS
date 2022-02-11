
<br />
<div align="center">
  <a href="https://github.com/ValentinSiegert/aTLAS">
    <img src="https://github.com/ValentinSiegert/aTLAS/raw/master/_logos/atlas_orange.svg" alt="aTLAS orange" height="80">
  </a>
  <h2>TrustLab</h2>
  <p>
    aTLAS – evaluating trust for autonomous web apps in a redecentralized web
    <!--<br />
    <a href="https://github.com/github_username/repo_name"><strong>Explore the docs »</strong></a> -->
    <br />
    <br />
    <a href="https://vsr.informatik.tu-chemnitz.de/projects/2020/atlas/demo/">View Demo</a>
    ·
    <a href="mailto:valentin.siegert@informatik.tu-chemnitz.de?subject=Issue on aTLAS">Report Bug</a>
    ·
    <a href="mailto:valentin.siegert@informatik.tu-chemnitz.de?subject=Question on aTLAS">Ask Question</a>
  </p>
</div>

<details open="open">
<summary>Table of Contents</summary>

- [About](#-about)
  - [Built With](#-built-with)
- [Getting Started](#-getting-started)
- [Usage](#-usage)
- [How To Scenario](#-how-to-scenario)
- [Authors & Contributors](#-authors--contributors)
- [Acknowledgements](#-acknowledgements)
- [Links To Know](#-links-to-know)

</details>


## 💡 About

<table>
<tr>
<td>

This is the main repository of the aTLAS testbed which includes the testbed's web server and director.
Therewith, all front-end capabilities are fully included, but not all back-end logic, which is derived
from the [submodule trustlab_host][atlas-host-repo].
The submodule is used as a library for certain models by the web server and the director and 
includes all aspects of the testbed environment with supervisor and interacting web agents.

> More details are to be found as well at the [project page][atlas-project].

<details>
<summary>Further Details</summary>

The redecentralization of the web introduces new challenges on trusting data from other sources
due to many unknown or even hidden parties.
An application working trustworthy in a decentralized web must evaluate trust and take trustaware decisions
autonomously without relying on a centralized infrastructure.
This autonomy and the huge amount of available applications necessitates the web to be modelled as
an open dynamic Multi-Agent System (MAS).
To evaluate the trust of web agents, the most suitable trust models need to be identified and used.
Despite the various trust models proposed in the literature for evaluating a web agent’s trust, 
the examination of them with different scenarios and configurations is not trivial.
To address these challenges, we initiated aTLAS, a Trust Laboratory of Multi-Agent Systems
which is a web-based wizard testbed for researchers and web engineers to evaluate trust models systematically.
aTLAS will enable future research regarding trust evaluations in a decentralized web.

The aTLAS project intends to examine trust for a redecentralization of the web.
It enables a broad comparison of trust mechanics, scales and models from the literature
within the current state of the art.
Therefore, it runs and evaluates multi-agent system scenarios, which are defined beforehand.
As the redencentralization of the web necessitates it to be modeled as a open dynamic multi-agent system,
such a laboratory can support the current situation where a comparision of trust approaches
for a decentralized web has to be done manually with a high effort.

> Relevant Publications:
> 
> [aTLAS: a Testbed to Examine Trust for a Redecentralized Web][atlas-paper]
> 
> [WTA: Towards a Web-based Testbed Architecture][wta-paper]

</details>
</td>
</tr>
</table>

### 🧱 Built With

1. Python 3.7
2. Django v2
3. Python pipenv
4. Redis Server
5. SQLite

## ⚡ Getting Started

> By default, please follow the local setup. The setup for VSRians is only for those knowing what they do there.

1. Install [Redis][redis-quickstart].

2. Clone Git Repository, [including all submodules][git-submodules].

3. Setup pipenv in project root:
    ```shell
    pipenv install
    ```
        
4. Modify ``Additional Options`` of your django configuration (for no auto-reload after editing scenario files) with:
    ```shell
    --noreload
    ```

5. Install also at least one supervisor, c.f. [submodule trustlab_host][trustlab-host-repo].

## 👟 Usage

> By default, please follow the local usage. The usage for VSRians is only for those knowing what they do there.

1. Run local Redis server in shell
    ```shell
    redis-server
    ```

3. Run aTLAS:
    ```bash
    python manage.py runserver 8000 --noreload
    ```

4. Run at least on supervisor with the [submodule trustlab_host][trustlab-host-repo] and connect it to aTLAS director.

## 📩 How To Scenario

- Scenario configurations can be placed in ``trustlab/lab/scenarios``.

- Every scenario configuration file has to end with ``_scenario.py``.

- All scenario parameters require to be the upperCase version of the respective ``Scenario.scenario_args`` arguments.

- Possible scenario arguments derive from ``Scenario.scenario_args`` arguments list, where parameters without default value are mandatory for scenario configuration file as well.

- You can make use of the scenario generation script at [_scenario_generation/](_scenario_generation/README.md) to generate larger scenarios.

## ✍ Authors & Contributors

The original setup of this repository is by the first author [Valentin Siegert][valentin-siegert-website].

All authors of this work in alphabetic order:

- [Martin Gaedke](https://vsr.informatik.tu-chemnitz.de/people/gaedke)
- Arved Kirchhoff
- [Mahda Noura](https://vsr.informatik.tu-chemnitz.de/people/mahdanoura)
- [Valentin Siegert][valentin-siegert-website]

## 👍 Acknowledgements

The authors acknowledge the work of the following students:

- Jun Li
- Marten Rogall


## 📚 Links To Know

* [aTLAS Project page][atlas-project]

* [Latest online prototype][atlas-demo]

* [Host Library Repository and Submodule at `trustlab_host`][atlas-host-repo]


<!-- Identifiers, in alphabetical order -->
[atlas-logo-orange]: https://github.com/ValentinSiegert/aTLAS/raw/master/_logos/atlas_orange.svg
[atlas-demo]: https://vsr.informatik.tu-chemnitz.de/projects/2020/atlas/demo/
[atlas-host-repo]: https://github.com/ValentinSiegert/aTLAS_host
[atlas-paper]: https://vsr.informatik.tu-chemnitz.de/research/publications/2020/010/
[atlas-project]: https://vsr.informatik.tu-chemnitz.de/projects/2020/atlas/
[git-submodules]: https://git-scm.com/book/en/v2/Git-Tools-Submodules
[redis-quickstart]: https://redis.io/topics/quickstart
[valentin-siegert-website]: https://vsr.informatik.tu-chemnitz.de/people/siegert
[wta-paper]: https://vsr.informatik.tu-chemnitz.de/research/publications/2021/007/
