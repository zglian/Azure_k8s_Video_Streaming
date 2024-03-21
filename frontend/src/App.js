import React from 'react';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { ChakraProvider, Box, theme } from '@chakra-ui/react';
import LoginPage from './LoginPage';
import Home from './Home';
import RegisterPage from './RegisterPage';
import AdminPage from './AdminPage';
import UserPage from './UserPage';
import WatchVideoPage from './WatchVideo';
import VideoUpload from './VideoUploader';

function App() {
  return (
    <ChakraProvider theme={theme}>
      <Box bg="gray.200" minH="100vh" py={8}>
        {/* <Text>{token}</Text> */}
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/admin" element={<AdminPage />} />
            <Route path="/user" element={<UserPage />} />
            <Route path="/video" element={<WatchVideoPage />} />
            <Route path="/upload" element={<VideoUpload />} />
          </Routes>
        </BrowserRouter>
      </Box>
    </ChakraProvider>
  );
}

export default App;
