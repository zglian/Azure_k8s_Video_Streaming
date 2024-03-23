'''@app.get("/previews/{url:path}")
async def video_endpoint(url: str):
    image_path = Path(f"./previews/{url}")
    return FileResponse(image_path, media_type="video/mp4")'''


'''@app.post("/upload/")
async def upload_video(video: UploadFile = File(...),
                       title: str = Form(),
                       description: str = Form(),
                       uploader_username: str = Form(),
                       db: Session = Depends(get_db)):
    contents = await video.read()
    upload_folder = "upload_videos"
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, video.filename)
    with open(file_path, "wb") as f:
        f.write(contents)
    new_video = Video(title=title,
                    description=description,
                    url=file_path,
                    uploader_username=uploader_username)
    db.add(new_video)
    db.commit()
    return new_video'''

'''@app.post("/upload-data/")
async def upload_video_data(video_upload: VideoModel, db: Session = Depends(get_db)):
    new_video = Video(title=video_upload.title,
                        description=video_upload.description,
                        url=video_upload.url)
    db.add(new_video)
    db.commit()

    # # 關聯上傳的視頻與用戶
    # new_video.usernames.append(username)
    # db.commit()
    return {"message": "Video uploaded successfully"}'''

'''def generate_preview_image(video_path: str, preview_image_path: str):
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    cv2.imwrite(preview_image_path, frame)
    cap.release'''
