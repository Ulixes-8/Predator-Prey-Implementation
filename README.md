# MSc Programming Skills Python predator-prey simulation

## Requirements

* Python 3.x
* [numpy](https://numpy.org/)
* [pytest](https://pytest.org/)

To get Python 3 on Cirrus, run:

```console
$ module load anaconda/python3
```

The Anaconda Python distribution includes numpy and many other useful Python packages.

---

## Usage

To see help:

```console
$ python -m predator_prey.simulate_predator_prey -h
```

To run the simulation:

```console
$ python -m predator_prey.simulate_predator_prey \
    [-r BIRTH_MICE] [-a DEATH_MICE] \
    [-k DIFFUSION_MICE] [-b BIRTH_FOXES] \
    [-m DEATH_FOXES] [-l DIFFUSION_FOXES] \
    [-dt DELTA_T] [-t TIME_STEP] [-d DURATION] \
    [-ls LANDSCAPE_SEED] [-lp LANDSCAPE_PROP] \
    [-lsm LANDSCAPE_SMOOTH] -f LANDSCAPE_FILE 
```

(where `\` denotes a line continuation character)

For example, to run using the default animal locations, [20x10.dat](../landscapes/20x10.dat), with default values for the other parameters:

```console
$ python -m predator_prey.simulate_predator_prey -f ../animals/20x10.dat
```

### Command-line parameters

| Flag | Parameter | Description | Default Value |
| ---- | --------- |------------ | ------------- |
| -h | --help | Show help message and exit | - |
| -r | --birth-mice | Birth rate of mice | 0.08 |
| -a | --death-mice | Rate at which foxes eat mice | 0.04 |
| -k | --diffusion-mice | Diffusion rate of mice | 0.2 |
| -b | --birth-foxes | Birth rate of foxes | 0.02 |
| -m | --death-foxes  | Rate at which foxes starve | 0.06 |
| -l | --diffusion-foxes | Diffusion rate of foxes | 0.2 |
| -dt | --delta-t | Time step size (seconds) | 0.4 |
| -t | --time_step | Number of time steps at which to output files | 10 |
| -d | --duration  | Time to run the simulation (seconds) | 500 |
| -ls | --landscape-seed | Random seed for initialising landscape | 1 |
| -lp | --landscape-prop | Average proportion of landscape that will initially be land | 0.75 |
| -lsm | --landscape-smooth | Number of smoothing passes after landscape initialisation | 2 |
| -f | --animal-file | Input animal location file | - |

### Input files

Animal location files are expected to be plain-text files of form:

* One line giving Nx, the number of columns, and Ny, the number of rows
* Ny lines, each consisting of a sequence of Nx space-separated two-digit integers (first digit = number of mice, second digit = number of foxes)

For example:

```
7 7
15 15 15 15 15 15 15
15 15 15 15 15 15 15
15 15 15 15 51 15 15
15 15 15 15 51 51 15
15 15 15 51 51 51 51
15 15 15 51 51 51 51
15 51 51 51 51 51 51
```

### PPM output files

"Plain PPM" image files are output every `TIME_STEP` timesteps.  These files are named `map_<NNNN>.ppm` and are a visualisation of the density of mice and foxes and water-only squares.

These files do not include the halo as the use of a halo is an implementation detail.

These files are plain-text so you can view them as you would any plain-text file e.g.:

```console
$ cat map<NNNN>.ppm
```

PPM files can be viewed graphically using ImageMagick commands as follows.

Cirrus users will need first need to run:

```console
$ module load ImageMagick
```

To view a PPM file, run:

```console
$ display map<NNNN>.ppm
```

To animate a series of PPM files:

```console
$ animate map*.ppm
```

For more information on the PPM file format, run `man ppm` or see [ppm](http://netpbm.sourceforge.net/doc/ppm.html).

### CSV averages output file

A plain-text comma-separated values file, `averages.csv`, has the average density of mice and foxes (across the land-only squares) calculated every `TIME_STEP` timesteps. The file has four columns and a header row:

```csv
Timestep,Time,Mice,Foxes
```

where:

* `Timestep`: timestep from 0 .. `DURATION` / `DELTA_T`
* `Time`: time in seconds from 0 .. `DURATION`
* `Mice`: average density of mice.
* `Foxes`: average density of foxes.

This file is plain-text so you can view it as you would any plain-text file e.g.:

```console
$ cat averages.csv
```

---

## Running automated tests

`test/test_example.py` is a module with a unit test for the `getVersion` function in `predator_prey/simulate_predator_prey.py`.

`pytest` can find and run any tests in the current directory or its subdirectories:

```console
$ pytest
======================================= test session starts =======================================
...
test/test_example.py .                                                                      [100%]

======================================== 1 passed in 0.20s ========================================
```

`pytest` can be told to find and run the tests in a specific module:

```console
$ pytest test/test_example.py
======================================= test session starts =======================================
...
test/test_example.py .                                                                      [100%]

======================================== 1 passed in 0.21s ========================================
```

`pytest` can be told to run a specific test within a specific module:

```console
$ pytest test/test_example.py::testGetVersion
======================================= test session starts =======================================
...
test/test_example.py .                                                                      [100%]

======================================== 1 passed in 0.35s ========================================
```

For more information on `pytest`, see the [pytest](https://docs.pytest.org/) documentation.

---

## Running the simulation within Pycharm

If you know how to use the [Pycharm](https://www.jetbrains.com/pycharm/) integrated development environment, then here is *one way* you can configure this to run the program and tests as follows (for example, for Pycharm 2020.02).

Start Pycharm.

Open the source code directory:

* Click Open
* Select the directory with the code, the directory with `predator_prey`, `test`, and `README.md`.

Create a configuration to run the program:

* Select Run menu, Run...
* Click Edit Configurations...
* Click +
* Click Python.
* Click V on right of 'Script path' and select 'Module name'.
* Enter Module name: `predator_prey.simulate_predator_prey`
* Enter Parameters: Enter `-f <path from your home directory to landscapes/10x20.dat>`. The current directory is assumed to be wherever you started Pycharm. If you started this in your home directory then your path to `landscapes/10x20.dat` might be `predator-prey-assessment/landscapes/10x20.dat`.
* Click Run.
* The 'Run' window should show the output from the run.

Rerun the program:

* Select Run menu, Run...
* Click `predator_prey.simulate_predator_prey`.
* The 'Run' window should show the output from the run.

Create a configuration to run the tests using `pytest`:

* Select Run menu, Run...
* Click Edit Configurations...
* Click +
* Click pytest.
* Click Run.
* The 'Run' window should show the output from the test run.

Rerun the tests:

* Select Run menu, Run...
* Click `predator_prey.simulate_predator_prey`.
* Click pytest.
* The 'Run' window should show the output from the test run.

To edit a run configuration:

* Select Run menu, Edit Configurations...
* Click the configuration you want to edit.
* For running `predator_prey.simulate_predator_prey` with different command-line parameters, you can add these to, and edit them within, the Parameters field in the Configuration form. Alternatively, you can create run configurations with different names for different parameter sets.
