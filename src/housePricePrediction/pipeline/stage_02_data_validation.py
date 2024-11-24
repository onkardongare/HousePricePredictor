from housePricePrediction.config.configuration import ConfigurationManager
from housePricePrediction.components.data_validation import DataValiadtion

STAGE = 'Data Validation Stage'

class DataValidationPipeline:
    def __init__(self):
        pass

    def main(self):
        config = ConfigurationManager()
        data_validation_config = config.get_data_validation_config()
        data_validation = DataValiadtion(config=data_validation_config)
        data_validation.validate_all_columns()
