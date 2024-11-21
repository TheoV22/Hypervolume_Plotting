Build on top of COCO repository : 
hyp_functions.py and main_plot.py are files that could be pushed to COCO repository to add a hypervolume visualisation option after running an experiment. 
It can help understanding the algorithm convergence to solutions as well as efficiency. 

archive_load_data.py and archive_exceptions.py are copied-pasted from their repository (re-use some of their code).
Experiments.ipynb simulate a use-case and can be run interactively : installing everything, running an experiment based on COCO test-suite, plotting hypervolume. 


Process : 

1) Open experiment.ipynb, run the test experiment code to create archive files.
2) Open a terminal window and run the command for main_plot.py
To know what command to run, open main_plot.py and modify the example command at the end of the file.
You can also run the plotting codes directly from experiments.ipynb to see directly the results.
