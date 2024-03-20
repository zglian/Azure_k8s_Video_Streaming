import { useState } from 'react';
import { Box, Button } from '@chakra-ui/react';
import { HOSTNAME } from './config.js';

function VideoUpload() {
  const [selectedFile, setSelectedFile] = useState(null);

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      console.error('No file selected');
      return;
    }

    try {
      const formData = new FormData();
      formData.append('video', selectedFile);

      const response = await fetch(`http://${HOSTNAME}/upload/`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      console.log('Upload successful');
    } catch (error) {
      console.error('Error uploading video:', error);
    }
  };

  return (
    <Box>
      <input type="file" accept="video/mp4" onChange={handleFileChange} />
      <Button onClick={handleUpload}>Upload Video</Button>
    </Box>
  );
}

export default VideoUpload;
