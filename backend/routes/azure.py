from fastapi import FastAPI, HTTPException, Header, Form, Depends, UploadFile, APIRouter
from sqlalchemy.orm import Session
from .models import *
import cv2
from .database import get_db
from azure.storage.blob import BlobServiceClient
from .config import *
import aiofiles
import os

router = APIRouter()

@router.post("/upload/image/")
async def upload_image_to_azure(video: UploadFile, 
                                title: str = Form(),
                                description: str = Form(),
                                uploader_username: str = Form()):
        file = video
        file_name = video.filename.replace('.mp4', '.jpg')
    # try:
        async with aiofiles.tempfile.NamedTemporaryFile("wb", delete=False) as temp:
            try:
                contents = await file.read()
                await temp.write(contents)
            except Exception:
                return {"message": "There was an error uploading the file"}
            finally:
                await file.close()
        cap = cv2.VideoCapture(temp.name)
        ret, frame = cap.read()
        ret, buffer = cv2.imencode('.jpg', frame)

        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        image_container_name = "image"

        async with blob_service_client:
            container_client = blob_service_client.get_container_client(image_container_name)
            image_blob_client = container_client.get_blob_client(file_name)
            await image_blob_client.upload_blob(buffer.tobytes(), overwrite = True)
        
        cap.release()
    # except Exception as e:
    #     return {"message": f"There was an error processing the file: {str(e)}"}
    # finally:
        os.remove(temp.name)
        return {"message": "Video processing completed successfully"}

async def upload_video_to_azure(file: UploadFile, file_name: str, file_type: str):
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    video_container_name = "video"
    
    async with blob_service_client:
            container_client = blob_service_client.get_container_client(video_container_name)
            try:
                video_blob_client = container_client.get_blob_client(file_name)
                f = await file.read()
                await video_blob_client.upload_blob(f, overwrite = True)
            except Exception as e:
                print(e)
                return HTTPException(401, "Something went terribly wrong..")
    return "{'did_it_work':'yeah it did!'}"

@router.post("/upload/video/")
async def create_upload_file(video: UploadFile, 
                            title: str = Form(),
                            description: str = Form(),
                            uploader_username: str = Form(),
                            db: Session = Depends(get_db)):
    #upload video data to db
    new_video = Video(title=title,
                    description=description,
                    url=video.filename,
                    uploader_username=uploader_username)
    db.add(new_video)
    db.commit()
    #upload video to azure
    video_name = video.filename
    type = video.content_type
    return await upload_video_to_azure(video, video_name, type)
    # image_name = video_name.replace('.mp4', '.jpg')
    # return await upload_image_to_azure(video, image_name)