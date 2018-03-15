# Microscope Setup for Corral Experiments
Author: Zachary Pincus  
Date: 2017-05-15  
http://zplab.wustl.edu

This brief tutorial describes how to set up an automated scope to acquire images from an assembled corral.

### Procedure:

1. Stop the jobs that are currently running on the scope (so that a job doesn’t start while you are setting things up) by running the following from a terminal:
       scope_job_runner stop

    If a job is currently running, a message will be displayed: "Waiting for job [JOB PATH] to complete.". After the job finishes, the program will print “Job complete. Job-runner is stopping.” and exit, returning control to the command line.

2. Open the scope box and place the corral onto the microscope stage. Check to make sure that a reference fluorescent microscope slide is loaded onto the scope stage.

3. Start the microscope server:
       scope_server start
      
    (If the scope server is already running, this will complain; that's fine.)

4. Start the microscope GUI:
       scope_gui

    If this fails, it could be problem with the scope server. To check it's status, run:
       scope_server status

    If necessary, restart the scope server:
       scope_server restart

5. Turn on the lamp and open up the transmitted light shutter from the scope GUI. Looking at your slide, move the stage such that the area of field illumination is over the first corral pad.

6. Set up Köhler illumination:  
  - Focus on the sample.
  - Close the field diaphragm.
  - Adjust the condenser focus so that the leaves of the diaphragm are in sharp focus.
  - Adjust the aperture diaphragm so that the back focal plane is 80% full.

7. Close the microscope box.

8. Toggle live mode on the scope GUI and set the exposure time to 1 or 2 ms.

9. Locate your slide with the stage controller.

10. Start ipython and run the following commands to get the list of corral slide and reference positions:
        from scope import scope_client; scope, scope_properties = scope_client.client_main() 
        from scope.timecourse import create_timecourse_dir
        slide_pos = create_timecourse_dir.simple_get_positions(scope)

    Use the stage controller and follow instructions to find positions to acquire from on the corral. Press control-c when all positions are acquired.

12. Locate the reference slide using the stage controller and record approximately 15 reference positions from clean areas of the reference slide:
        ref_pos = create_timecourse_dir.simple_get_positions(scope)

    Note: If you record unwanted positions, continue gathering all desired positions. After getting all the positions, the undesired positions can be deleted from the list with standard Python syntax:
        del slide_pos[x] 
        del slide_pos[x:y]

13. using the above position lists, create the timecourse metadata file:
        data_dir = '/path/to/your/desired/job/directory'
        z_max = 25.7 # or whatever z-position the stage should not advance past
        create_timecourse_dir.create_metadata_file(data_dir, slide_pos, z_max, ref_pos)

14. If you don't have an acquisition file to copy over to the directory, create one:
        create_timecourse_dir.create_acquire_file(data_dir, run_interval, filter_cube, fluorescence_flatfield_lamp=None)

    where the parameters are as follows:
    - `run_interval`: desired number of hours between starts of timepoint
        acquisitions.
    - `filter_cube`: name of the filter cube to use
    - `fluorescence_flatfield_lamp`: if fluorescent flatfield images are
        desired, provide the name of an appropriate spectra x lamp that is
        compatible with the specified filter cube.

    After this you can exit ipython.

15. Turn off live mode and the lamp in the scope GUI, and then close the GUI.

16. Use the scope job runner to add your experiment to the queue:
        scope_job_runner add /path/to/your/desired/job/directory/acquire.py youremail@wustl.edu

17. Restart the scope job runner:
        scope_job_runner start

18. Check scope job runner status (confirm that your experiment was added): 
        scope_job_runner status