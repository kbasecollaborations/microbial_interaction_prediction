# -*- coding: utf-8 -*-
#BEGIN_HEADER
import logging
import os

from installed_clients.KBaseReportClient import KBaseReport
from microbial_interaction_prediction.Utils.AntibacterialUtils import AntibacterialUtils
from installed_clients.WorkspaceClient import Workspace as workspaceService
#END_HEADER


class microbial_interaction_prediction:
    '''
    Module Name:
    microbial_interaction_prediction

    Module Description:
    A KBase module: microbial_interaction_prediction
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "0.0.1"
    GIT_URL = ""
    GIT_COMMIT_HASH = ""

    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.shared_folder = config['scratch']
        self.ws_url = config["workspace-url"]
        logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                            level=logging.INFO)
        self.config = config
        #END_CONSTRUCTOR
        pass


    def run_microbial_interaction_prediction(self, ctx, params):
        """
        This example function accepts any number of parameters and returns results in a KBaseReport
        :param params: instance of mapping from String to unspecified object
        :returns: instance of type "ReportResults" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN run_microbial_interaction_prediction
        print ("####################\n")
        print (params)
        print ("####################\n")

        genome_input_refs = params['genome_refs']

        genome_refs = list()
        for genome_input_ref in genome_input_refs:
            wsClient = workspaceService(self.ws_url, token=ctx['token'])
            genome_info = wsClient.get_object_info_new({'objects': [{'ref': genome_input_ref}]})[0]
            genome_input_type = genome_info[2]

            if 'GenomeSet' in genome_input_type:
                genomeSet_object = wsClient.get_objects2({'objects': [{'ref': genome_input_ref}]})['data'][0]['data']
                for ref_dict in genomeSet_object['elements'].values():
                    genome_refs.append(ref_dict['ref'])
            else:
                genome_refs.append(genome_input_ref)



        genome_refs = list(set(genome_refs))
        print (genome_refs)

       
        no_SSN = "True" if params['no_SSN']==1 else "False"

        f = AntibacterialUtils(self.config, params)
        output = f.run_antibacterial_main(genome_refs, no_SSN)
        print (output)

        #END run_microbial_interaction_prediction

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method run_microbial_interaction_prediction return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
