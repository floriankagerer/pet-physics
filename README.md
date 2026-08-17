<h1 align="center">
<img src="branding/pet-physics-wallpaper.png" width="1000">
</h1><br>

<div align="center">

# PET-Physics: A Packing Evaluation Tool Considering Physics

</div>

---

<!-- -------------------------------------------------------------- -->
## <div align="center">Paper Accepted</div>
I am happy to announce that our paper "PET-Physics: A Packing Evaluation Tool Considering Physics" has been accepted for publication in the proceedings of the <a href="https://2026.ieeecase.org/" target="_blank">2026 IEEE 22nd International Conference on Automation Science and Engineering</a> in Shenyang, China.


Whenever you use our tool, please cite our publication:

>
> F. Enzenhofer, J. Ondřej, and A. Nüchter. PET-Physics: A Packing Evaluation Tool Considering Physics. TBA
> <br>
> <a href=".bib" target="_blank">[BibTeX]</a>
<a href="https://doi.org" target="_blank">[DOI]</a>
>

<!-- -------------------------------------------------------------- -->
## <div align="center">Getting Started</div>

The recommended Python setup is as follows:
- Python 3.12
- Create virtual environment using `Anaconda`
- Install `poetry` for managing dependencies
- Run command `poetry config virtualenvs.create false` to avoid that `poetry` creates virtual environments.
- Run `poetry install`

<!-- -------------------------------------------------------------- -->
## <div align="center">In a nutshell</div>
Without having a robotic bin packing setup, the prediction whether a packing plan results in a stable pallet is based
on an informed guess based on prior experience. Since such a setup is costly, for many algorithms it is unclear
if they are suitable for production. To close this gap, we provide our simulation framework PET-Physics that enables
researchers to assess a solver’s quality. Based on the pose recording of all bodies, it is possible to check not only
for static stability, but also dynamic stability of a packing plan. A novel feature of our tool is the provision of
data that supports the detection of boxes that might be overloaded. 

<!-- -------------------------------------------------------------- -->
## <div align="center">Scripts</div>
Demo scripts for different applications are in the folder [examples](./examples/).
