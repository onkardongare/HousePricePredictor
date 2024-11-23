import os 
import urllib.request as request
import tarfile
import zipfile
from housePricePrediction import logger
from housePricePrediction.utils.common import get_size
from housePricePrediction.entity.config_entity import *

class DataIngestion:
    def __init__(self, config: DataIngestionConfig):
        self.config = config


    def download_file(self):
        if not os.path.exists(self.config.local_data_file):
            filename,headers = request.urlretrieve(
                url = self.config.source_URL,
                filename = self.config.local_data_file
            )
            logger.info(f"{filename} download! with following info: \n{headers}")
        else:
            logger.info(f"File already exists of size: {get_size(Path(self.config.local_data_file))}")

        
    def extract_zip_file(self):
        """ 
        zip_file_path: str
        Extracts the zip file into the data directory
        Function returns None
        """
        
        os.makedirs(self.config.unzip_dir, exist_ok=True)
        with zipfile.ZipFile(self.config.local_data_file, 'r') as zip_ref:
            zip_ref.extractall(self.config.unzip_dir)

    def extract_tgz_file(self):
        """ 
        Extracts a .tgz file to specific directory.
        """
        with tarfile.open(self.config.local_data_file,'r:gz') as tar:
            tar.extractall(path= self.config.unzip_dir)
        