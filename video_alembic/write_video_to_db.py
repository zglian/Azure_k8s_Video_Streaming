from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from models import User, Video, UserVideo, Base

# 創建資料庫引擎
engine = create_engine('postgresql://postgres:test@localhost:5432/postgres')

# 創建表
Base.metadata.create_all(engine)

# 創建會話
Session = sessionmaker(bind=engine)
session = Session()

# 讀取影片檔案的二進位數據
video_file_path = 'video_dataset/video-4.mp4'  # 更新為影片檔案的正確路徑
with open(video_file_path, 'rb') as f:
    video_data = f.read()

# 創建 Video 對象並保存到資料庫中
new_video = Video(video_id = 4, title='Beautiful scene', description='good scene', video_data=video_data)
session.add(new_video)
session.commit()

# 關閉會話
session.close()
