from housePricePrediction.config.configuration import ConfigurationManager
from housePricePrediction.components.data_transformation import DataTransformation
from housePricePrediction import logger
from pathlib import Path


STAGE_NAME = "Data Transformation Stage"

class DataTransformationPipeline:
    def __init__(self):
        pass

    def main(self):
        try:
            with open(Path("artifacts/data_validation/status.txt"),"r") as f:
                status = f.read().split(" ")[-1]

            if status == "True":
                config = ConfigurationManager()
                data_transformation_config = config.get_data_transformation_config()
                data_transformation = DataTransformation(config=data_transformation_config)
                housing = data_transformation.train_test_splitting()
                preprocessing = data_transformation.preprocessing_pipeline()
                housing_prepared = preprocessing.fit_transform(housing)
                return housing_prepared
            else:
                raise Exception("Your data is not valid")
            
        except Exception as e:
            print(e)