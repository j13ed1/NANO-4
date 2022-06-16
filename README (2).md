This project uses the power of datalake on AWS platform.

What is a data lake?
A data lake is a repository that allows you to store all your structured and unstructured data. 

In order to run the ETL pipeline, we need to setup the Spark environment and create the SparkSession. 

Setup EMR Cluster (using emr 5.20.0)


The project contains the following components:

etl.py reads data from S3
the dl.cfg contains
AWS_ACCESS_KEY_ID=<your_aws_access_key_id>
AWS_SECRET_ACCESS_KEY=<your_aws_secret_access_key>
