# -*- coding: utf-8 -*-
"""
Created on Mon Aug 15 12:20:56 2022

@author: kscamp3
"""

import os
import sys
import json
import copy

import numpy as np

from pathlib import Path

sys.path.append('c:/ken/github/campbellmusclelab/models/fibersim/code/fiberpy/fiberpy/package/modules/protocols')
sys.path.append('c:/ken/github/campbellmusclelab/models/fibersim/code/fiberpy/fiberpy/package/modules/analysis')

import protocols as p
import curve_fitting as cf

def characterize_permeabilized_models():
    """ Characterize models """
    
    # 1 = Null
    # 2 = Stabilized SRX
    # 3 = Stabilized SRX and sensitized k_on
    
    k_2_mod = [1, 3, 3]
    k_on_mod = [1, 1, 3]

    # Variables
    base_model_file_string = '../simulations/a/base/base_model.json'
    base_setup_file_string = '../simulations/a/base/permeabilized_setup.json'


    FiberSim_code_dir = 'c:/ken/github/campbellmusclelab/models/fibersim/code/fiberpy/fiberpy'
    batch_mode = 'characterize'
    
    generated_model_file_base = '../permeabilized/generated/model'
    generated_setup_file_string = '../permeabilized/generated/generated_setup.json'
    
    # Load the base setup and base model
    with open(base_setup_file_string, 'r') as f:
        base_setup = json.load(f) 

    with open(base_model_file_string, 'r') as f:
        base_model = json.load(f)
        
    # Get the parent dir, because all paths have to be converted to absolutes
    base_dir = Path(base_setup_file_string).parent.absolute()
        
    # Loop through mod factors
    rep_model_file_strings = list()
    
    for i in range(len(k_2_mod)):

        # Copy the base model
        rep_model = copy.deepcopy(base_model)

        # myosin drx to srx
        y = np.asarray(rep_model['m_kinetics'][0]['scheme'][1]['transition'][0]['rate_parameters'],
                       dtype=np.float32)
        y = y * k_2_mod[i]
        rep_model['m_kinetics'][0]['scheme'][1]['transition'][0]['rate_parameters'] = \
            y.tolist()

        # k_on
        y = np.asarray(rep_model['thin_parameters']['a_k_on'],
                       dtype=np.float32)
        y = y * k_on_mod[i]
        rep_model['thin_parameters']['a_k_on'] = y
               
        # Generate a model file name
        rfs = ('%s_%i.json' % (generated_model_file_base, i+1))
        
        # Correct path
        rfs = str(Path(os.path.join(base_dir, rfs)).resolve())
        
        # Make the directory if required
        rfs_dir = Path(rfs).parent
        if not os.path.isdir(rfs_dir):
            os.makedirs(rfs_dir)

        # Write the model
        with open(rfs, 'w') as f:
            json.dump(rep_model, f, indent=4)
            
        # Convert to absolute path
        rfs = str(Path(os.path.join(base_dir, rfs)).resolve())

        # Add in to array
        rep_model_file_strings.append(rfs)
    
    # Now copy the setup
    generated_setup = copy.deepcopy(base_setup)
    
    # And change the file names to absolute paths
    generated_setup['FiberSim_characterization']['model']['relative_to'] = 'false'
    generated_setup['FiberSim_characterization']['model']['model_files'] = rep_model_file_strings
    generated_setup['FiberSim_characterization']['model']['options_file'] = \
        str(Path(os.path.join(base_dir,
                              generated_setup['FiberSim_characterization']['model']['options_file'])).resolve())
    
    # Loop through the characterizations, changing these paths
    characterize = generated_setup['FiberSim_characterization']['characterization']
    for i,c in enumerate(characterize):
        c['relative_to'] = 'false'
        c['sim_folder'] = str(Path(os.path.join(base_dir,
                                                c['sim_folder'])).resolve())
        generated_setup['FiberSim_characterization']['characterization'][i] = c

    # And finally the setup file
    generated_setup_file_string = str(Path(os.path.join(base_dir,
                                                        generated_setup_file_string)).resolve())
    
    print("\n\n%s\n\n" % generated_setup_file_string)
    
    with open(generated_setup_file_string, 'w') as f:
        json.dump(generated_setup, f, indent=4)
        
    # Generate a command line
    cs = 'pushd \"%s\" & python FiberPy.py %s %s & popd' % \
            (FiberSim_code_dir, batch_mode, generated_setup_file_string)
    
    # And run it
    os.system(cs)
    
def characterize_living_models():
    """ Characterize models with electrically-evoked twitches """
    
    # 1 = Null
    # 2 = Stabilized SRX
    # 3 = Stabilized SRX and sensitized k_on
    
    k_2_mod = [1, 3, 3]
    k_on_mod = [10, 10, 30]
    
    n_points = 1000
    dt = 0.001
    start_t = 0.1
    stim_freq = [1,5,10]

    # Variables
    base_setup_file_string = '../simulations/a/base/living_setup.json'
    base_model_file_string = '../simulations/a/base/base_model.json'

    FiberSim_code_dir = 'c:/ken/github/campbellmusclelab/models/fibersim/code/fiberpy/fiberpy'
    batch_mode = 'characterize'
    
    generated_model_file_base = '../living/generated/model'
    generated_setup_file_string = '../living/generated/generated_setup.json'
    
    # Load the base setup and base model
    with open(base_setup_file_string, 'r') as f:
        base_setup = json.load(f) 

    with open(base_model_file_string, 'r') as f:
        base_model = json.load(f)
        
    # Get the parent dir, because all paths have to be converted to absolutes
    base_dir = Path(base_setup_file_string).parent.absolute()
    
    # Generate force frequency protocols
    twitch_prot_dir = Path(os.path.join(base_dir,
                                   Path(generated_model_file_base).parent,
                                   'protocol',
                                   'force_freq')).absolute()
    print(twitch_prot_dir)
    if not os.path.isdir(twitch_prot_dir):
        os.makedirs(twitch_prot_dir)
    
    t = np.cumsum(dt * np.ones(n_points))
    for i,stim_f in enumerate(stim_freq):
        
        stim_t = []
        t_s = 0.1
        stim_t.append(t_s)
        
        t_step = (1.0 / stim_f)
        keep_going=True
        while keep_going:
            t_s = t_s + t_step
            if (t_s < np.amax(t)):
                stim_t.append(t_s)
            else:
                keep_going=False
                
        df = p.create_twitch_protocol(time_step = dt,
                                      n_points = n_points,
                                      stimulus_times_s = stim_t)

        twitch_prot_file = os.path.join(twitch_prot_dir,
                                        'force_freq_%i.txt' % i)
        df.to_csv(twitch_prot_file, sep='\t', index=None)                    
        
    # Loop through mod factors
    rep_model_file_strings = list()
    
    for i in range(len(k_on_mod)):

        # Copy the base model
        rep_model = copy.deepcopy(base_model)

        # myosin drx to srx
        y = np.asarray(rep_model['m_kinetics'][0]['scheme'][1]['transition'][0]['rate_parameters'],
                       dtype=np.float32)
        y = y * k_2_mod[i]
        rep_model['m_kinetics'][0]['scheme'][1]['transition'][0]['rate_parameters'] = \
            y.tolist()

        # k_on
        y = np.asarray(rep_model['thin_parameters']['a_k_on'],
                       dtype=np.float32)
        y = y * k_on_mod[i]
        rep_model['thin_parameters']['a_k_on'] = y
               
        # Generate a model file name
        rfs = ('%s_%i.json' % (generated_model_file_base, i+1))
        
        # Correct path
        rfs = str(Path(os.path.join(base_dir, rfs)).resolve())
        
        print(rfs)

        # Write the model
        with open(rfs, 'w') as f:
            json.dump(rep_model, f, indent=4)
            
        # Convert to absolute path
        rfs = str(Path(os.path.join(base_dir, rfs)).resolve())

        # Add in to array
        rep_model_file_strings.append(rfs)
    
    # Now copy the setup
    generated_setup = copy.deepcopy(base_setup)
    
    # And change the file names to absolute paths
    generated_setup['FiberSim_characterization']['model']['relative_to'] = 'false'
    generated_setup['FiberSim_characterization']['model']['model_files'] = rep_model_file_strings
    generated_setup['FiberSim_characterization']['model']['options_file'] = \
        str(Path(os.path.join(base_dir,
                              generated_setup['FiberSim_characterization']['model']['options_file'])).resolve())
    
    # Loop through the characterizations, changing these paths
    characterize = generated_setup['FiberSim_characterization']['characterization']
    for i,c in enumerate(characterize):
        c['relative_to'] = 'false'
        c['sim_folder'] = str(Path(os.path.join(base_dir,
                                                c['sim_folder'])).resolve())
        generated_setup['FiberSim_characterization']['characterization'][i] = c

    # And finally the setup file
    generated_setup_file_string = str(Path(os.path.join(base_dir,
                                                        generated_setup_file_string)).resolve())
    
    print("\n\n%s\n\n" % generated_setup_file_string)
    
    with open(generated_setup_file_string, 'w') as f:
        json.dump(generated_setup, f, indent=4)
        
    # Generate a command line
    cs = 'pushd \"%s\" & python FiberPy.py %s %s & popd' % \
            (FiberSim_code_dir, batch_mode, generated_setup_file_string)
    
    # And run it
    os.system(cs)    
    

if __name__ == "__main__":
    characterize_permeabilized_models()
    #characterize_living_models()
