# phonotactics

This is the Inductive Projection Learner. 

It currently does two things, both of which require running the Maxent Phonotactic Learner developed by Colin Wilson. See his Github (colincwilson) for maxent.jar; the version bundled with this should be identical.

You need to have Java 8 installed on your computer. You also need to have Python 3 (at least 3.5).

Quick help: navigate to the 'code' folder. Type 

$ python3 run_sim.py quechua/roots wb gain50 ncons100


(If you are on "windows", use the backwards slash). 

This will run the inductive projection learner on the Quechua roots file inside the data directory. If you want to try other data, put it in the data folder, with a unique language name. You need to have LearningData.txt and Features.txt files, formatted as for the UCLA Phonotactic Learner of Hayes and Wilson 2008. If you do not have your own TestingData.txt file, the learner will make its own from 1/5th of your training data.

If the learner succeeds, your simulation results will appear inside the sims folder, along with a "program trace" that describes the overall steps of the projection induction part of the learner. The results of individual learner runs will be in subolders inside the main simulation folder. 

If something goes wrong and the learner does not give you an informative error message, check the contents of maxent2/temp/maxentoutput.txt. This is the file that captures the output of the java learner, which would otherwise have been printed to screen.

For further options, enter "python3 run_sim.py help" at the bash prompt (or wherever you're able to run python scripts).
