import React, { useState, useEffect } from 'react';
import {
  Box,
  Text,
  VStack,
  Center,
  HStack,
  Image,
  Spacer,
  Link,
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
      console.log(data);
      setVideos(data.videos);
    }
    fetchVideos();
  }, []);

  const handleVideoClick = async video => {
    // setShowVideo(false);
    console.log(selectedButton);
    if (selectedButton === video.title) {
      setSelectedButton('');
      setShowVideo(false);
      setUrl('');
    } else {
      setShowVideo(false);
      setTimeout(() => {
        setShowVideo(true);
      }, 1);
      setSelectedButton(video.title);
      setUrl(video.url);
    }
  };

  return (
    <Center minH="80vh">
      <Link
        href="/"
        position="absolute"
        top="14px"
        left="14px"
        fontSize="20px"
        color="teal.500"
      >
        Back
      </Link>
      {showVideo ? (
        <HStack spacing={8} marginTop="40px">
          {/* 影片清單 */}
          <Box w="35%" pl="25px">
            <VStack spacing={5} align="flex-start">
              <Text
                fontFamily="Arial, sans-serif"
                fontSize="26px"
                color="teal.500"
                fontWeight="md"
              >
                影片清單
              </Text>
              <Box w="100%">
                <HStack spacing={5} wrap="wrap">
                  {videos.map((video, index) => (
                    <Box
                      key={index}
                      borderWidth="1px"
                      borderRadius="md"
                      overflow="hidden"
                      cursor="pointer"
                      width="200px" // Adjust as needed to control number of boxes per row
                      marginBottom="3" // Add margin to separate the boxes
                      borderColor={
                        selectedButton === video.title ? 'teal.500' : 'gray.300'
                      }
                      _hover={{ borderColor: 'teal.500' }}
                      onClick={() => {
                        handleVideoClick(video);
                      }}
                    >
                      <Box>
                        <Image
                          src={`http://${HOSTNAME}/previews/${video.preview_url}`}
                          alt={video.title}
                          width="100%"
                          height="100%"
                          objectFit="cover"
                        />
                      </Box>
                      <Box p="4">
                        <Text fontSize="md" wordBreak="break-word">
                          {video.title}
                        </Text>
                      </Box>
                    </Box>
                  ))}
                </HStack>
              </Box>
            </VStack>
          </Box>
          <Spacer />
          {/* 影片播放器 */}
          <Box w="75%">
            <Box>
              <video width="850" controls autoPlay muted>
                <source
                  src={`http://${HOSTNAME}/video/${url}`}
                  type="video/mp4"
                />
              </video>
            </Box>
          </Box>
        </HStack>
      ) : (
        <VStack spacing={8} align="center">
          <Text
            fontFamily="Arial, sans-serif"
            fontSize="26px"
            color="teal.500"
            fontWeight="bold"
          >
            影片清單
          </Text>
          <Box w="100%">
            <HStack spacing={8} wrap="wrap" justifyContent="center">
              {videos.map((video, index) => (
                <Box
                  key={index}
                  borderWidth="1px"
                  borderRadius="md"
                  overflow="hidden"
                  cursor="pointer"
                  width="400px"
                  align="center"
                  borderColor="gray.400"
                  _hover={{ borderColor: 'teal.500' }}
                  onClick={() => {
                    handleVideoClick(video);
                  }}
                  marginBottom="8px" // Add some bottom margin to separate the boxes
                >
                  <Image
                    src={`http://localhost:8000/previews/${video.preview_url}`}
                    alt={video.title}
                    width="100%"
                    height="100%"
                    objectFit="cover"
                  />
                  <Box p="4">
                    <Text
                      fontSize="light"
                      fontWeight="semibold"
                      wordBreak="break-word"
                    >
                      {video.title}
                    </Text>
                  </Box>
                </Box>
              ))}
            </HStack>
          </Box>
        </VStack>
      )}
    </Center>
  );
}

export default WatchVideoPage;
