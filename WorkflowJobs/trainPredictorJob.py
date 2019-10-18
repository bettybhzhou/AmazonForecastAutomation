import sys
import boto3
import datetime
from awsglue.utils import getResolvedOptions

session = boto3.Session(region_name='us-west-2') 
forecast = session.client(service_name='forecast') 
glue_client = session.client(service_name='glue')

dt = datetime.datetime.now()
project = 'inventory_forecast_' + dt.strftime('%d_%m_%y')
predictorName= project + '_AutoML'
forecastHorizon = 2
workflowName = 'AmazonForecastWorkflow'
workflow = glue_client.get_workflow(Name=workflowName)
workflow_params = workflow['Workflow']['LastRun']['WorkflowRunProperties']
workflowRunId = workflow['Workflow']['LastRun']['WorkflowRunId']
datasetGroupArn = workflow_params['datasetGroupArn']


create_predictor_response=forecast.create_predictor(PredictorName=predictorName, 
                                                ForecastHorizon=forecastHorizon,
                                                PerformAutoML= True,
                                                PerformHPO=False,
                                                EvaluationParameters= {"NumberOfBacktestWindows": 1, 
                                                                        "BackTestWindowOffset": 2}, 
                                                InputDataConfig= {"DatasetGroupArn": datasetGroupArn},
                                                FeaturizationConfig= {"ForecastFrequency": "15min", 
                                                                    "Featurizations": 
                                                                    [
                                                                        {"AttributeName": "demand", 
                                                                        "FeaturizationPipeline": 
                                                                        [
                                                                            {"FeaturizationMethodName": "filling", 
                                                                            "FeaturizationMethodParameters": 
                                                                            {"frontfill": "none", 
                                                                                "middlefill": "zero", 
                                                                                "backfill": "zero"}
                                                                            }
                                                                        ]
                                                                        }
                                                                    ]
                                                                    }
                                                    )
predictorArn=create_predictor_response['PredictorArn']

workflow_params['predictorArn'] = predictorArn
glue_client.put_workflow_run_properties(Name=workflowName, RunId=workflowRunId, RunProperties=workflow_params)
workflow_params = glue_client.get_workflow_run_properties(Name=workflowName,
                                        RunId=workflowRunId)["RunProperties"]

print('output Predictor Arn is: ' + workflow_params['predictorArn'])
