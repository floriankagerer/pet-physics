Contains MJCF files that are reused in the simulation.

When you create a MJCF file that are stored in this directory, make sure that you

1. include them in your actual model with `<include file=... />.
2. add a parent tag, e.g., `<worldbody></worldboday>` around the objects you want since the MuJoCo compiler 
   removes the topmost tag when including the file.
