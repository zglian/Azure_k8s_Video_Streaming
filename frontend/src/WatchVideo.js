// // import React from 'react';

// function WatchVideoPage() {
//   return (
//     <div>
//       <video width="1200" controls muted>
//         <source src="http://localhost:8000/video/video-1/" type="video/mp4" />
//       </video>
//     </div>
//   );
// }

// // export default WatchVideoPage;

import React, { useState, useEffect } from 'react';
import {
  Box,
  Text,
  Button,
  VStack,
  Center,
  HStack
} from '@chakra-ui/react';
import { HOSTNAME } from './config.js';

function WatchVideoPage() {
  const [videos, setVideos] = useState([]);
  const [url, setUrl] = useState('');
  const [showVideo, setShowVideo] = useState(false);
  const [selectedButton, setSelectedButton] = useState(null);

  // 從後端獲取影片清單
  useEffect(() => {
    async function fetchVideos() {
      const response = await fetch(`http://${HOSTNAME}/videos/`);
      const data = await response.json();
      setVideos(data.videos);
    }
    fetchVideos();
  }, []);

  const handleVideoClick = async (video) => {
    // setShowVideo(false);
    console.log(selectedButton)
    if(selectedButton === video.title){
        setSelectedButton("")
        setShowVideo(false)
        setUrl('')
    }
    else{
        setShowVideo(false)
        setTimeout(() => {
            setShowVideo(true)
        }, 100)
        setSelectedButton(video.title)
        setUrl(video.url);
    }
  };

  return (
    <Center minH="80vh">
        <HStack spacing={100} align="flex-start">
            <VStack spacing={4} align="center">
                <Text
                fontFamily="Arial, sans-serif"
                fontSize="32px"
                color="teal.500"
                fontWeight="bold"
                >
                影片清單
                </Text>
                <Box w="80%">
                {/* Video List */}
                <VStack spacing={2}>
                    {videos
                        // .sort((a, b) => a.title.localeCompare(b.title))
                        .map((video, index) => (
                        <Button 
                            key={index} 
                            colorScheme={selectedButton === video.title ? 'teal' : 'gray'}
                            onClick={() => {
                                handleVideoClick(video)
                            }}
                        >
                            {video.title}
                        </Button>
                    ))}
                </VStack>
                </Box>
            </VStack>

            {/* 影片播放器 */}
            {showVideo && (
            <Box>
                <video width="500" controls autoPlay muted>
                <source src={`http://localhost:8000/video/${url}`} type="video/mp4" />
                </video>
            </Box>
            )}
      </HStack>
    {/* <div>
       <video width="1200" controls muted>
         <source src="http://localhost:8000/video/video-4.mp4/" type="video/mp4" />
      </video>
    </div> */}
    </Center>
    
  );
}

export default WatchVideoPage;

