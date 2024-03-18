import React, { useState } from 'react';
import {BrowserRouter, Route, Routes } from "react-router-dom";
import {
  ChakraProvider,
  Box,
  theme,
} from '@chakra-ui/react';
import LoginPage from './LoginPage';
import Home from './Home';
import RegisterPage from './RegisterPage';
import AdminPage from './AdminPage';
import UserPage from './UserPage';

function App() {
  const [token, setToken] = useState(''); 
  return (
    <ChakraProvider theme={theme}>
      <Box bg="gray.200" minH="100vh" py={8}>
        {/* <Text>{token}</Text> */}
          <BrowserRouter>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/login" element={<LoginPage setNewToken={setToken}/>} />
              <Route path="/register" element={<RegisterPage />} />
              <Route 
                path="/admin"
                element={<AdminPage token={token} />} 
              />
              <Route path="/user" element={<UserPage token={token} />} />
            </Routes>
          </BrowserRouter>
      </Box>
    </ChakraProvider>
  );
}

export default App;
