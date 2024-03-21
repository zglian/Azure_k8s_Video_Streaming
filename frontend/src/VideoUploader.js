import { useState, useEffect } from 'react';
import {
  Box,
  Text,
  Input,
  Button,
  VStack,
  Link,
  Textarea,
} from '@chakra-ui/react';
import { HOSTNAME } from './config.js';

function VideoUpload() {
  const [message, setMessage] = useState('');
  const token = sessionStorage.getItem('token');
  const [selectedFile, setSelectedFile] = useState(null);
  const [videoData, setVideoData] = useState({
    // video_id: '',
    title: '',
    description: '',
    url: '',
    uploader_username: '',
  });

  useEffect(() => {
    const verifyTokenHandler = async () => {
      try {
        const response = await fetch(`http://${HOSTNAME}/verify`, {
          method: 'POST',
          headers: {
            token: token,
          },
        });
        if (response.ok) {
          const user = await response.json();
          console.log('User:', user);
          setVideoData(prevState => ({
            ...prevState,
            uploader_username: user.username,
          }));
        } else {
          console.error('Token verification failed');
        }
      } catch (error) {
        console.error('Error verifying token:', error);
      }
    };

    verifyTokenHandler();

    // Clean-up function to prevent memory leaks
    return () => {
      // Any clean-up code if needed
    };
  }, [token]);

  if (!videoData.uploader_username) {
    return (
      <VStack>
        <Text fontSize="24px">Please log in to upload videos.</Text>
        <Link href="/login" color="teal.500" fontSize="20px">
          Go to Login Page
        </Link>
      </VStack>
    );
  }

  const handleFileChange = event => {
    setSelectedFile(event.target.files[0]);
  };
  const handleTitleChange = event => {
    setVideoData({ ...videoData, title: event.target.value });
    setMessage('');
  };
  const handleDescriptionChange = event => {
    setVideoData({ ...videoData, description: event.target.value });
  };
  const handleLogout = () => {
    sessionStorage.removeItem('token');
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      console.error('No file selected');
      return;
    }

    try {
      const formData = new FormData();
      formData.append('video', selectedFile);
      formData.append('title', videoData.title);
      formData.append('description', videoData.description);
      // formData.append('url', videoData.url);
      formData.append('uploader_username', videoData.uploader_username);

      console.log(formData);
      await fetch(`http://${HOSTNAME}/upload`, {
        method: 'POST',
        body: formData,
      });
      setVideoData({
        ...videoData,
        title: '',
        description: '',
        url: '',
      });
      setMessage('Upload Success!');
    } catch (error) {
      console.error('Error uploading video:', error);
    }
  };

  return (
    <VStack minH="80vh" alignItems="center" marginTop="100px" spacing={4}>
      <Link
        href="/user"
        position="absolute"
        top="14px"
        left="14px"
        fontSize="20px"
        color="teal.500"
      >
        Back
      </Link>
      <Link
        onClick={handleLogout}
        position="absolute"
        top="14px"
        right="14px"
        href="/"
      >
        Logout
      </Link>
      <Box>
        <Text
          fontFamily="Arial, sans-serif"
          fontSize="25px"
          color="teal.500"
          fontWeight="bold"
          mb={4}
        >
          Upload Video
        </Text>
        <Input
          type="text"
          placeholder="Enter video title"
          value={videoData.title}
          onChange={handleTitleChange}
          mb={4}
          variant={'outline'}
          borderColor={'teal'}
        />
        <Textarea
          placeholder="Enter video description"
          value={videoData.description}
          onChange={handleDescriptionChange}
          mb={4}
          variant={'outline'}
          borderColor={'teal'}
        />
        <Box mt={2}>
          <input type="file" accept="video/mp4" onChange={handleFileChange} />
        </Box>
        <Button
          mt={4}
          onClick={handleUpload}
          isDisabled={
            videoData.description === '' ||
            videoData.title === '' ||
            !selectedFile
          }
        >
          Upload Video
        </Button>
        <Text mt="2" fontSize="15px" color="red" fontWeight="light">
          {message}
        </Text>
      </Box>
    </VStack>
  );
}

export default VideoUpload;
