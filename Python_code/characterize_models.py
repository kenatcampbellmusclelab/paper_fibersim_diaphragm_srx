# -*- coding: utf-8 -*-
"""
Created on Mon Aug 15 12:20:56 2022

@author: kscamp3
"""

import os
import json
import copy

import numpy as np

from pathlib import Path

def characterize_models():
    """ Characterize models """
    
    # 1 = Null
    # 2 = Stabilized SRX
    # 3 = Stabilized SRX and sensitized k_on
    
    k_2_mod = [1, 3, 3]
    k_on_mod = [1, 1, 3]

    # Variables
    base_setup_file_string = '../simulations/a/base/base_setup.json'
    base_model_file_string = '../simulations/a/base/base_model.json'

    FiberSim_code_dir = 'd:/ken/github/campbellmusclelab/models/fibersim/code/fiberpy/fiberpy'
    batch_mode = 'characterize'
    
    generated_model_file_base = '../generated/model'
    generated_setup_file_string = '../generated/generated_setup.json'
    
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
    characterize_models()
