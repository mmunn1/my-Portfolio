import boto3
import StringIO
import zipfile
import mimetypes


s3 = boto3.resource('s3')

build_bucket = s3.Bucket('portfoliobuild')
portfolio_bucket = s3.Bucket('portfolio.michael.munn')

portfolio_zip = StringIO.StringIO()
build_bucket.download_fileobj('portfoliobuild.zip', portfolio_zip)

with zipfile.ZipFile(portfolio_zip) as myzip:
    for nm in myzip.namelist():
        print nm
        obj = myzip.open(nm)
        portfolio_bucket.upload_fileobj(obj,nm,
            ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
        portfolio_bucket.Object(nm).Acl().put(ACL='public-read')
