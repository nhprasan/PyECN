| :exclamation: This repository is no longer actively developed or maintained.  :exclamation: |
|-----------------------------------------|

# PyECN

PyECN is a python-based equivalent circuit network (ECN) framework for modelling lithium-ion batteries.

## Framework overview

An Equivalent Circuit Network (ECN) represents a complex electrochemical system using
standard electrical components (e.g., resistors and capacitors) to approximate its
behavior without explicitly modeling all internal physics. PyECN extends this idea by
discretizing a cell into many coupled electrical and thermal sub-units, enabling
spatially resolved electro-thermal simulation for pouch, cylindrical, and prismatic
form factors.

At runtime, PyECN loads a TOML configuration, prepares lookup tables (LUTs), builds the
cell model, and advances the coupled electrical + thermal solvers over time.

## Using PyECN

PyECN is run by providing `pyecn` with a configuration file for a simulation, containing details of a cell's geometrical, physical, electrical and thermal properties, as well as operating conditions. An example configuration file for a pouch cell is provided in `cylindrical.toml`:

```bash
$ python -m pyecn cylindrical.toml
```

PyECN can also be run in an interactive python session:

```bash
$ python
>>> import pyecn
>>> pyecn.run()
Enter config file name:
cylindrical.toml
```

### Live visualization with custom current profiles

You can run live electro-thermal visualization (surface temperature heatmap + time series)
by providing a current profile CSV via the CLI. The CSV must contain headers `t_s,I_A`
with monotonic time (duplicate times are allowed for piecewise-constant steps). Use
`--dt` to control the solver time step and `--t_end` to override the simulation duration
if desired.

Example:

```bash
python -m pyecn cylindrical.toml --profile mixed.csv --dt 1 --t_end 200
```

Notes:

* If `--profile` is a relative path, PyECN first checks the current working directory,
  then falls back to `pyecn/Examples/Profiles/`.
* Positive current is discharge, negative current is charge.

## Installing PyECN

<details>
  <summary>Linux/macOS</summary>

  1. Clone the repository and enter the directory:
  ```bash
  git clone https://github.com/ImperialCollegeLondon/PyECN.git
  cd PyECN
  ```

  2. Create and activate a virtual environment:
  ```bash
  python -m venv .venv
  source .venv/bin/activate
  ```

  3. Install the dependencies:
  ```bash
  pip install -U pip
  pip install -r requirements.txt
  ```

  4. Run a simulation (example):
  ```bash
  python -m pyecn cylindrical.toml --profile mixed.csv --dt 1 --t_end 200
  ```
</details>

<details>
  <summary>Windows</summary>

  1. Clone the repository and enter the directory:
  ```bat
  git clone https://github.com/ImperialCollegeLondon/PyECN.git
  cd PyECN
  ```

  2. Create and activate a virtual environment:
  ```bat
  python -m venv .venv
  .venv\Scripts\activate.bat
  ```

  3. Install the dependencies:
  ```bat
  pip install -U pip
  pip install -r requirements.txt
  ```

  4. Run a simulation (example):
  ```bat
  python -m pyecn cylindrical.toml --profile mixed.csv --dt 1 --t_end 200
  ```
</details>

## Citing PyECN

If you use PyECN in your work, please cite our paper

> Li, S., Rawat, S. K., Zhu, T., Offer, G. J., & Marinescu, M. (2023). Python-based Equivalent Circuit Network (PyECN) Model-ling Framework for Lithium-ion Batteries: Next generation open-source battery modelling framework for Lithium-ion batteries. _Engineering Archive_.

You can use the BibTeX

```
@article{lipython,
  title={Python-based Equivalent Circuit Network (PyECN) Model-ling Framework for Lithium-ion Batteries: Next generation open-source battery modelling framework for Lithium-ion batteries},
  author={Li, Shen and Rawat, Sunil Kumar and Zhu, Tao and Offer, Gregory J and Marinescu, Monica},
  publisher={Engineering Archive}
}
```

## Contributing to PyECN

TBC


## License

PyECN is fully open source. For more information about its license, see [LICENSE](https://github.com/ImperialCollegeLondon/PyECN/blob/add_license/LICENSE.md).


## Contributors

- Shen Li: Conceptualisation, methodology, creator and lead developer of PyECN, writing and review;
- Sunil Rawat: Contributor of PyECN, discussion, writing and review;
- Tao Zhu: Contributor of PyECN, discussion, writing and review;
- Gregory J Offer: Conceptualisation, funding acquisition, supervision, writing – review & editing;
- Monica Marinescu: Conceptualisation, funding acquisition, supervision, writing – review & editing;
