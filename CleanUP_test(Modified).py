# import pyodbc
# import sys
# import urllib3
import pymssql
import sys
import boto3
from urllib.parse import urlparse
import re

appname = sys.argv[1]  ##without mlflow_
usr = sys.argv[2]
pwd = sys.argv[3]
bucket_name = sys.argv[4]
schema_name = appname
#************Connection String*******************# 
conn = pymssql.connect(host='FE0SQC36.de.bosch.com', port='56518',user=usr,password=pwd,database='DB_MLFlow_Prodenv_SQL')
#conn = pyodbc.connect(driver='{ODBC Driver 17 for SQL Server}', server='tcp:FE0SQC36.de.bosch.com,56518', database='DB_MLFlow_Prodenv_SQL', uid=usr, pwd=pwd, trusted_connection='yes')

c = conn.cursor()
exp_row = c.execute("SELECT experiment_id FROM ["+ schema_name +"].[experiments] where lifecycle_stage='deleted'")
exp_rows = c.fetchall()
exp_count=len(exp_rows)
print ("Deleted Experiments:",exp_count)


run_row = c.execute("SELECT artifact_uri FROM ["+ schema_name +"].[runs] where lifecycle_stage='deleted'")
run_rows = c.fetchall()
run_count=len(run_rows)
print ("Deleted Runs:",run_rows)

print ("Number of deleted runs : ",run_count)


# define tables to delete from
tables = ['params', 'metrics','latest_metrics','tags','runs']
# define the SQL query to delete rows
# If a whole experiment is deleted
sql_query = "DELETE FROM ["+ schema_name +"].{} WHERE run_uuid IN (SELECT run_uuid FROM ["+ schema_name +"].runs where experiment_id IN (SELECT experiment_id FROM ["+ schema_name +"].[experiments] where lifecycle_stage='deleted'))"
sql_query2= "DELETE FROM ["+ schema_name +"].[experiments] WHERE lifecycle_stage='deleted'"

# to remove deleted runs
sql_query3 = "DELETE FROM ["+ schema_name +"].{} WHERE run_uuid IN (SELECT run_uuid FROM ["+ schema_name +"].runs where lifecycle_stage='deleted')"



#Registered Models can be deleted from WebUI
#******************************S3 Connection********#
urllib3.disable_warnings()

 # in pipeline mention mlflow-<app-name>
#s3_client = boto3.client('s3')
session = boto3.session.Session()


aws_access_key_id = 'key'
aws_secret_access_key = 'Key'
s3_client = session.client(
    service_name='s3',
    #aws_ca_bundle='s3.pem',
    aws_access_key_id = aws_access_key_id ,
    aws_secret_access_key = aws_secret_access_key,

    endpoint_url='https://rb-objectstorage.de.bosch.com:9021',
    use_ssl=True,
    verify=False
    )
s3storage = boto3.resource('s3',
    aws_access_key_id = aws_access_key_id ,
    aws_secret_access_key = aws_secret_access_key,
    
    endpoint_url='https://rb-objectstorage.de.bosch.com:9021',
    use_ssl=True,
    verify=False
    )

my_bucket=s3storage.Bucket(bucket_name)
#*************************************************************************#
def IsObjectExists(path):
    for object_summary in my_bucket.objects.filter(Prefix=path):
        return True
    return False

#********************************

### Function defination for deleting artifact
def delete_artifacts(s3_client, bucket_name, prefix):
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    try:
        for object in response['Contents']:
            if IsObjectExists(object['Key']):
                print('Deleting', object['Key'])
                #s3_client.delete_object(Bucket=bucket_name, Key=object['Key'])
            else:
                print("Artifact does not exist")
                print('Deleting the folder', object['Key'])
    except KeyError:
        print("Artifacts not available")






## To delete Runs and experiments######

if (exp_count > 0) and (run_count <= 0) :
    # only experiment names / runns associated with deleted experiments

    for table in tables:

        cursor = conn.cursor()
        print(table)
        print(schema_name)
        #cursor.execute(sql_query.format(table))
        print(f'{cursor.rowcount} rows deleted from {table}')
        
    #cursor.execute(sql_query2) # delete from experiment table
    print(f'{cursor.rowcount} rows deleted from experiments')    

    print("(exp_count > 0) and (run_count <= 0) only exp")

    for exp_row in exp_rows:
        print("Experiment_id:", exp_row)
        PREFIX = 'mlartifacts/{}'.format(exp_row[0])
        #function call
        delete_artifacts(s3_client, bucket_name, PREFIX)  
            
            
            
elif (exp_count > 0) and (run_count > 0) :  
    
#to delete all the deleted entries from runs and onther table
    
    # loop through tables and execute delete query
    for table in tables:

        cursor = conn.cursor()
        print("Table Name : ",table)
        cursor.execute(sql_query3.format(table))
        print(f'{cursor.rowcount} rows deleted from {table}')
   

    for run_row in run_rows:
                  
        text=urlparse('{}'.format(run_row[0])).path
        print("Artifact Path: ",text)
        print("text",text)
        PREFIX = 'mlartifacts'+ text
        print("S3 Path of runs", text)
        #function call  
        delete_artifacts(s3_client, bucket_name, PREFIX)
            
    c = conn.cursor()
    exp_row = c.execute("SELECT experiment_id FROM ["+ schema_name +"].[experiments] where lifecycle_stage='deleted'")
    exp_rows = c.fetchall()
    exp_count=len(exp_rows)
    print ("Deleted Experiments:",exp_count)    
    
    
    cursor.execute(sql_query2)
    print(f'{cursor.rowcount} rows deleted from experiments')    #Delete only the experiment table




elif (exp_count <= 0) and (run_count > 0) :  
    print("(exp_count < 0) and (run_count >= 0)")
    # loop through tables and execute delete query
    for table in tables:

        cursor = conn.cursor()
        print("Table Neme : ",table)
        cursor.execute(sql_query3.format(table))
        print(f'{cursor.rowcount} rows deleted from {table}')

    for run_row in run_rows:
                  
        text=urlparse('{}'.format(run_row[0])).path
        print("Artifact Path: ",text)
        PREFIX = 'mlartifacts'+ text


        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=PREFIX)
        print(response)
        try:
            for object in response['Contents']:
                if(IsObjectExists(object['Key'])):
                #print("Directory/File exists")
                    print('Deleting', object['Key'])
                    s3_client.delete_object(Bucket=bucket_name, Key=object['Key'])
                else:
                    print("Artifact doesnot exist")
                    print('Deleting the folder', object['Key'])
        except KeyError:
            print("Artifacts not available")
        
           
else:
    print("No tables to be cleaned up")
    
print("Execution Completed")    

    
    #-------------------------------------------------------------#
#-------------------Close Connection-----------------------------#
conn.commit()
conn.close()

print(f'Successfully cleaned up data base & artifacts')
 