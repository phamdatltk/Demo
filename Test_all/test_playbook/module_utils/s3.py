def upload_to_s3(client, local_file, bucket, s3_file):
    try:
        client.upload_file(local_file, bucket, s3_file)
        print("Upload Successful", s3_file)
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False

def delete_object(client, bucket, folder):
    list_object = client.list_objects(Bucket=bucket, Prefix=folder)
    for item in [obj['Key'] for obj in list_object.get('Contents', [])]:
        # print(item)
        client.delete_object(Bucket=bucket, Key=item)
    print("Delete Successful", folder)
    return True


def archive_file_object(client, dest_bucket, source_file, s3_file):
    client.copy_object(
        Bucket=dest_bucket,
        CopySource=source_file,
        Key=s3_file,
    )
    # print(response)
    # print("Archive Successful", s3_file)
    return True

def archive_folder_object(client, source_bucket, dest_bucket, folder):
    list_object = client.list_objects(Bucket=source_bucket, Prefix=folder)
    for item in [obj['Key'] for obj in list_object.get('Contents', [])]:
        print(item)
        source_file = {'Bucket': source_bucket,'Key': item}
        client.copy_object(Bucket=dest_bucket, CopySource=source_file, Key=folder + item[len(folder):])
    print("Archived Successful")
    return True