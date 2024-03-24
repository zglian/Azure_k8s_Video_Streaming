import pygame
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Video, Base

# 創建資料庫引擎
engine = create_engine('postgresql://postgres:test@localhost:5432/postgres')

# 創建表
Base.metadata.create_all(engine)

# 創建會話
Session = sessionmaker(bind=engine)
session = Session()

# 從資料庫中檢索影片的二進位數據
video = session.query(Video).filter_by(title='Writing notes and using a laptop').first()
video_data = video.video_data

# 將影片的二進位數據寫入到暫存檔案中
temp_video_file_path = 'temp_video.mp4'
with open(temp_video_file_path, 'wb') as f:
    f.write(video_data)

# 初始化 pygame
pygame.init()

# 設置影片顯示窗口大小
screen = pygame.display.set_mode((800, 600))

# 播放影片
pygame.mixer.music.load(temp_video_file_path)
pygame.mixer.music.play()

print("video start")

# 等待影片播放結束
while pygame.mixer.music.get_busy():
    pygame.time.Clock().tick(10)

print("video end")

# 刪除暫存檔案
pygame.mixer.quit()
pygame.quit()
