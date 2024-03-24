# Fullend Video Streaming System

## Overview

This is a video playback system that consists of two roles: users and administrators. Users can register accounts, upload videos, and watch videos. Administrators have the ability to view all users and perform management tasks.

## Architecture

### Deployment

- **Cloud Provider**: Azure
- **Container Orchestration**: Kubernetes (Azure Kubernetes Service)
- **Object Storage**: Azure Blob Storage

### Frontend

- **Framework**: React.js
- **UI Library**: Chakra UI

### Backend

- **Framework**: FastAPI
- **Authentication**: OAuth2

### Database

- **Database**: PostgreSQL
- **Database Migration**: Alembic
- **Deployment**: Helm

## Feature

basic function

login as user, login as admin, modify data...

<img src="img/login.jpg" alt="Login" width="300">

watch video

<img src="img/video-1.jpg" alt="Video 1" width="300">
<img src="img/video-2.jpg" alt="Video 2" width="300">

upload video

<img src="img/upload.jpg" alt="Upload" width="300">

## Demo Video

[Demo Video(Click Here)](https://youtu.be/MZd8qqe7Zww)

Register Account -> Log In -> View User Data -> Update Data -> Watch Video -> Upload Video -> Watch Uploaded Video -> Log Out

Admin Log In -> View Users -> Delete User
