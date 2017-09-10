import boto3
import StringIO
import zipfile
import mimetypes
import boto3
import sys


def lambda_handler(event, context):
    s3 = boto3.resource('s3')
    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:us-west-2:423708827346:deployPortfolioTopic')

    location = {
        "bucketName" : 'portfolio.michael.munn',
        "objectKey" : 'portfoliobuild.zip'
    }
    try:
        job = event.get('CodePipeline.job')
        if job:
            for artifact in job['data']['inputArtifacts']:
                if artifact['name'] == 'MyAppBuild':
                    location = artifact['location']['s3Location']

        print 'Building Portfolio from ' + str(location)

        portfolio_bucket = s3.Bucket('portfolio.michael.munn')
        build_bucket = s3.Bucket('portfoliobuild')

        portfolio_zip = StringIO.StringIO()
        build_bucket.download_fileobj('portfoliobuild.zip', portfolio_zip)

        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj,nm,
                    ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')
        topic.publish(Subject='Portfolio Deployed Successfully', Message='Nice!')
        print 'Job Done'

        if job:
            codepipeline = boto3.client('codepipeline')
            codepipeline.put_job_success_result(jobId=job['id'])

    except Exception as err:
        topic.publish(Subject="Portfolio Deploy Failed", Message=str(err))
        raise


    return 'Hello from Lambda'
