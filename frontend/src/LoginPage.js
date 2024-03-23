import React, { useState } from 'react';
import {
  Box,
  Text,
  Input,
  Button,
  VStack,
  Center,
  Link,
} from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';
import { HOSTNAME } from './config.js';

function LoginPage({ setNewToken }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  const handleLogin = async () => {
    await fetch(`http://${HOSTNAME}/login`, {
      // mode: 'no-cors',
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: `username=${username}&password=${password}`,
    })
      .then(response => {
        if (response.ok) {
          return response.json();
        } else {
          setMessage(`Login failed`);
        }
      })
      .then(data => {
        if (data) {
          const token = data.token;
          // console.log(data.token);
          sessionStorage.setItem('token', token);
          // setNewToken(token);
          if (username === 'admin') {
            navigate('/admin');
          } else {
            navigate('/user');
          }
        }
      });
    setTimeout(() => {
      setMessage('');
    }, 500);
  };

  return (
    <Center minH="80vh">
      <VStack spacing={4} align="center">
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
        <Text
          fontFamily="Arial, sans-serif"
          fontSize="32px"
          color="teal.500"
          fontWeight="bold"
        >
          Log in to your account
        </Text>
        <Input
          type="text"
          placeholder="Username"
          value={username}
          onChange={e => setUsername(e.target.value)}
          variant={'outline'}
          borderColor={'teal'}
          onKeyDown={e => {
            if (e.key === 'Enter' && username !== '' && password !== '') {
              e.preventDefault(); // Prevent form submission
              handleLogin(); // Call the delete function
            }
          }}
        />
        <Input
          type="password"
          placeholder="Password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          variant={'outline'}
          borderColor={'teal'}
          onKeyDown={e => {
            if (e.key === 'Enter' && username !== '' && password !== '') {
              e.preventDefault(); // Prevent form submission
              handleLogin(); // Call the delete function
            }
          }}
        />
        <Text fontSize="8px" color="red" minHeight="20px">
          {message}
        </Text>
        <Button
          colorScheme="teal"
          fontFamily="Arial, sans-serif"
          isDisabled={username === '' || password === ''}
          onClick={() => handleLogin()}
        >
          Login
        </Button>
        <Box>
          New to us?{' '}
          <Link
            color="teal.500"
            fontFamily="Arial, sans-serif"
            href="/register"
          >
            Sign Up
          </Link>
        </Box>
      </VStack>
    </Center>
  );
}

export default LoginPage;
