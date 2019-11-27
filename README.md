# AIXI ANU 2019

Implements the Monte Carlo AIXI agent with [context tree weighting](https://ieeexplore.ieee.org/document/382012), a computable approximation of [AIXI](https://en.wikipedia.org/wiki/AIXI), and tests it in a wide variety of game environments.

The agent is based on [(Veness *et al*, 2011)](http://www.jveness.info/publications/jair2010%20-%20mc_aixi_approx.pdf). A [skeletal implementation by G. Kassel](https://github.com/gkassel/pyaixi) was given by the instructor, upon which we added most of the meat.

#### Authors

This is a group project for [COMP4620: Advanced Topics in Artificial Intelligence, in Australian National University, 2019 Semester 2](https://archive.is/egsGB). The group started with six people, but two dropped out early on. The remaining four people contributed roughly equally.

#### File structure

-   `pyaixi`: Python code that implements AIXI.
-   `report`: LaTeX and images that are used to generate the final report.
-   Folders that end in `conf`: Configuration files used in testing the agent.
