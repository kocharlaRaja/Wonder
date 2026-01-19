# pip install azure-storage-blob


import os
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError
import tkinter as tk
from tkinter import filedialog


def create_container_if_not_exists(blob_service_client, container_name):
    try:
        container_client = blob_service_client.get_container_client(container_name)
        if not container_client.exists():
            container_client.create_container()
            print(f"New container '{container_name}' created.")
        else:
            print(f"All good container '{container_name}' already exists.")
    except Exception as e:
        print(f"Failed to create or check container: {e}")


def upload_blob(blob_service_client, container_name, local_file_path, blob_name):
    try:
        blob_client = blob_service_client.get_blob_client(
            container=container_name, blob=blob_name
        )
        with open(local_file_path, "rb") as data:
            blob_client.upload_blob(data)
        print(
            f"File {local_file_path} uploaded to {blob_name} in container {container_name}."
        )
    except Exception as e:
        print(f"Failed to upload file: {e}")


def list_blobs(blob_service_client, container_name):
    try:
        container_client = blob_service_client.get_container_client(container_name)
        blobs = container_client.list_blobs()
        blob_list = [blob.name for blob in blobs]
        return blob_list
    except Exception as e:
        print(f"Failed to list blobs: {e}")
        return []


def download_blob(blob_service_client, container_name, blob_name, download_file_path):
    try:
        blob_client = blob_service_client.get_blob_client(
            container=container_name, blob=blob_name
        )
        with open(download_file_path, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())
        print(f"File {blob_name} downloaded to {download_file_path}.")
    except ResourceNotFoundError:
        print(f"The blob {blob_name} does not exist.")
    except Exception as e:
        print(f"Failed to download blob: {e}")


def delete_blob(blob_service_client, container_name, blob_name):
    try:
        blob_client = blob_service_client.get_blob_client(
            container=container_name, blob=blob_name
        )
        blob_client.delete_blob()
        print(f"Blob {blob_name} deleted from container {container_name}.")
    except ResourceNotFoundError:
        print(f"The blob {blob_name} does not exist.")
    except Exception as e:
        print(f"Failed to delete blob: {e}")


def main():
    azure_storage_name = input("Storage Account Name: ")
    azure_storage_key = input("Storage Account Key: ")
    container_name = input("Container Name (e.g. uploads): ")

    try:
        blob_service_client = BlobServiceClient(
            account_url=f"https://{azure_storage_name}.blob.core.windows.net",
            credential=azure_storage_key,
        )
    except Exception as e:
        print(f"Failed to create BlobServiceClient: {e}")
        return

    create_container_if_not_exists(blob_service_client, container_name)

    # Initialize Tkinter root (hidden)
    root = tk.Tk()
    root.withdraw()

    while True:
        print("\nOptions:")
        print("1. Upload a file")
        print("2. Download or delete a file")
        print("3. Exit")
        option = input("Enter your choice: ")

        if option == "1":
            local_file_path = filedialog.askopenfilename(title="Select file to upload")
            if not local_file_path:
                print("No file selected.")
                continue
            blob_name = os.path.basename(local_file_path)
            upload_blob(blob_service_client, container_name, local_file_path, blob_name)
        elif option == "2":
            blobs = list_blobs(blob_service_client, container_name)
            if blobs:
                print("Blobs in container:")
                for i, blob in enumerate(blobs, 1):
                    print(f"{i}. {blob}")
                blob_choice = (
                    int(input("Enter the number of the blob to download or delete: "))
                    - 1
                )
                if 0 <= blob_choice < len(blobs):
                    blob_name = blobs[blob_choice]
                    print("Options:")
                    print("1. Download")
                    print("2. Delete")
                    action = input("Enter your choice: ")
                    if action == "1":
                        download_file_path = input(
                            "Enter the local path to download the file to: "
                        )
                        download_blob(
                            blob_service_client,
                            container_name,
                            blob_name,
                            download_file_path,
                        )
                    elif action == "2":
                        delete_blob(blob_service_client, container_name, blob_name)
                    else:
                        print("Invalid choice.")
                else:
                    print("Invalid blob number.")
            else:
                print("No blobs found in the container.")
        elif option == "3":
            print("Exiting...")
            break
        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    main()
