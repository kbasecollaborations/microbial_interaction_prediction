import time
import os
import errno
import uuid
import shutil
import stat
import gzip
from zipfile import ZipFile, ZIP_DEFLATED
import subprocess  # nosec

from installed_clients.GenomeFileUtilClient import GenomeFileUtil
from installed_clients.AssemblyUtilClient import AssemblyUtil
from installed_clients.DataFileUtilClient import DataFileUtil
from installed_clients.WorkspaceClient import Workspace
from installed_clients.KBaseReportClient import KBaseReport

ANTIBACTERIAL_SCRIPT = "/kb/module/lib/microbial_interaction_prediction/Utils/run_antibacterial.sh"

def log(message, prefix_newline=False):
    time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time()))
    print(('\n' if prefix_newline else '') + time_str + ': ' + message)

class AntibacterialUtils:


    def __init__(self, config, params):
        self.ws_url = config["workspace-url"]
        self.callback_url =os.environ['SDK_CALLBACK_URL']
        self.scratch = config['scratch']

        self.dfu = DataFileUtil(self.callback_url)
        self.gfu = GenomeFileUtil(self.callback_url)
        self.au = AssemblyUtil(self.callback_url)
        self.report = KBaseReport (self.callback_url)
        
        self.workspace_name = params['workspace_name']
    def _mkdir_p(self, path):
        """
        _mkdir_p: make directory for given path
        """
        if not path:
            return
        try:
            os.makedirs(path)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise

    def delete_zip (self,path):
        dir_list = os.listdir(path)
        for j in dir_list:
            if j.endswith(".zip"):
                zipfilename = os.path.join(path,j)
                os.remove(zipfilename)

     

    def get_genome_folder_name(self,genome_ref):
        ws=Workspace(self.ws_url)
        obj = { "ref": genome_ref }
        obj_info = ws.get_object_info3({
            "objects": [obj],
            "includeMetadata": 1
            })

        obs=genome_ref.replace("/", "_")
        return (obj_info['infos'][0][1] + "_" +  str(obs))

    def get_gff_path(self,download_ret):
       gff_file_path = download_ret.get('file_path')
       return gff_file_path
    def get_assembly_path (self,download_ret):
       for j in download_ret:
          return (download_ret[j]['paths'][0]) # return the first instance
    
    def get_fasta_gff_file_path(self, genome_ref):
         genome_folder_name = self.get_genome_folder_name(genome_ref)
         result_dir = os.path.join (self.scratch, genome_folder_name)
         self._mkdir_p(result_dir)

         #Download fasta
         download_params2 = {'ref_lst': [genome_ref]}
         download_ret2 = self.au.get_fastas(download_params2)
         print (download_ret2)
         fasta_file_path = self.get_assembly_path(download_ret2)
         print (fasta_file_path)
         fasta_file_name = os.path.basename(fasta_file_path)
         shutil.move(fasta_file_path, result_dir)
         n_fasta_file_path = os.path.join(result_dir, fasta_file_name)
         return {"fasta":n_fasta_file_path} 


    def run_antibacterial_multiple(self, output_dir , fasta_file_paths):

        fasta_files = " ".join(fasta_file_paths)
        argstring =  ANTIBACTERIAL_SCRIPT + " "   +  output_dir + " " + fasta_files
        print (argstring)
        args = argstring.split(" ")
        proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # nosec
        (stdout, stderr) = proc.communicate()
        print('-' * 80)
        print('Antibacterial output:')
        print(stdout)
        print(stderr)
        print('-' * 80)
        if proc.returncode != 0:
            raise Exception(f"Error generating Antismash output: {stderr}")

        return output_dir


    def add_html_page(self, output_dir, html_string):
        try:
            with open(output_dir +"/index.html" , "w") as html_file:
               html_file.write(html_string +"\n") 
        except IOError:
            print("Unable to write to "+  output_dir + "/index.html" + " file on disk.")
 
        

    def create_html_report(self, output_dir, workspace_name):
        '''
        function for creating html report
        :param callback_url:
        :param output_dir:
        :param workspace_name:
        :return:
        '''

        report_name = 'antibacterial_report_' + str(uuid.uuid4())

        report_shock_id = self.dfu.file_to_shock({'file_path': output_dir,
                                            'pack': 'zip'})['shock_id']

        html_file = {
            'shock_id': report_shock_id,
            'name': 'index.html',
            'label': 'index.html',
            'description': 'HTML report for Antismash'
            }
        
        report_info = self.report.create_extended_report({
                        'direct_html_link_index': 0,
                        'html_links': [html_file],
                        'report_object_name': report_name,
                        'workspace_name': workspace_name
                    })
        return {
            'report_name': report_info['name'],
            'report_ref': report_info['ref']
        }

    
    def run_antibacterial_main(self,genome_refs):
            analysis_dir = os.path.join(self.scratch, str(uuid.uuid4()))
            result_dir = os.path.join(self.scratch, str(uuid.uuid4()))

            self._mkdir_p(analysis_dir)
            self._mkdir_p(result_dir)

            genome_fasta_paths = list()  
            for genome_ref in genome_refs:
                g_download = self.get_fasta_gff_file_path(genome_ref)
                fasta_file_path = g_download.get('fasta')
                genome_fasta_paths.append(fasta_file_path)

            output_dir = self.run_antibacterial_multiple(analysis_dir, genome_fasta_paths) 
            aggregate_html = os.path.join(analysis_dir, "aggregated_results.html")
            index_html = os.path.join(result_dir, "index.html")
            shutil.copy(aggregate_html, index_html)
            output = self.create_html_report(result_dir, self.workspace_name)            
            return output


