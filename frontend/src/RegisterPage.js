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
import { HOSTNAME } from './config.js';

function RegisterPage(){
    const [message, setMessage] = useState('');
    const [createUserData, setCreateUserData] = useState({
        username: '',
        password: '',
        birthday: '',
      });

    const handleCreateUser = async () => {
      await fetch(`http://${HOSTNAME}/user/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(createUserData),
      })
        .then((response) => {
        if (response.ok){
            setMessage(`User ${createUserData.username} created`);
            setCreateUserData({username: '', password: '', birthday:''});
        }            
        else
            setMessage(`User ${createUserData.username} already exists`);
        })    
  };


  return(
    <Center minH="80vh">
        <VStack spacing={4}  align="center">
            <Link href='/' position="absolute" top="14px" left="14px" fontSize="20px" color="teal.500">
               Back
            </Link>
            <Text 
              fontFamily="Arial, sans-serif"
              fontSize="32px"
              color="teal.500"
              fontWeight="bold"
            >
              Enter User Data
            </Text>
            <Input
              type="text"
              placeholder="Username"
              value={createUserData.username}
              onChange={(e) =>
                setCreateUserData({...createUserData, username: e.target.value,
                })
              }
              variant={'outline'}
              borderColor={'teal'}
            />
            <Input
              type="password"
              placeholder="Password"
              value={createUserData.password}
              onChange={(e) =>
                setCreateUserData({...createUserData, password: e.target.value,
                })
              }
              variant={'outline'}
              borderColor={'teal'}
            />
            <Input
              type="text"
              placeholder="Birthday (yyyy-mm-dd)"
              value={createUserData.birthday}
              onChange={(e) =>
                setCreateUserData({...createUserData, birthday: e.target.value,
                })
              }
              variant={'outline'}
              borderColor={'teal'}
            />
            <Box h="4px" />
            <Button 
              colorScheme="teal" 
              width="150px" 
              onClick={handleCreateUser}
              isDisabled={createUserData.username === "" || createUserData.password ==="" || createUserData.birthday === ""}
            >
              Confirm
            </Button>
            <Text 
              fontSize="8px"
              color="black"
              fontWeight="light"
            >
              {message} 
            </Text>
        </VStack>
    </Center>
  );
}

export default RegisterPage;