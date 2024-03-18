import React, { useState } from 'react';
import {
  Box,
  Text,
  Input,
  Button,
  VStack,
  Link,
  HStack,
} from '@chakra-ui/react';
import { HOSTNAME } from './config.js';

function UserPage(props){
    const token = props.token;
    const [userData, setUserData] = useState({
        username: '',
        password: '',
        birthday: '',
        last_login: '',
        create_time: '',
    });
    const [updateUserData, setUpdateUserData] = useState({
        username: '',
        password: '',
        birthday: '',
    });
    const [showUserData, setShowUserData] = useState(false);
    const [showUpdate, setShowUpdate] = useState(false);
    const [message, setMessage] = useState('');

    if(!token){
        return(
            <VStack>
                <Text fontSize="24px">Please log in to access the user page.</Text>
                <Link href="/login" color="teal.500" fontSize="20px">Go to Login Page</Link>
            </VStack>
        );
    }

    const handleGetUser = async () => {
        await fetch(`http://${HOSTNAME}/user/`, {
        method: 'GET',
        headers: {
            Authorization: token,
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        })
        .then((response) => {
            if (response.ok) {
                return response.json();
            }else{
                throw new Error('Get user failed');
            }
        })
        .then((data) => {
            setUserData(data.user);
        })
        .catch((error) => {
            console.error(error);
        });
    };

    const handleUpdateUser = async () => {
        try {
        await fetch(`http://${HOSTNAME}/user/`, {
            method: 'PATCH',
            headers: {
            'Content-Type': 'application/json',
            Authorization: token,
            },
            body: JSON.stringify(updateUserData),
        });
        setMessage('User updated');
        setUpdateUserData({password: '', birthday:''});
        } catch (error) {
        setMessage('Unauthorized');
        }
    };

    return(
        <VStack minH="80vh" alignItems="center" marginTop="100px">
            <VStack spacing={4} align="center">
                <Link href='/' position="absolute" top="14px" left="14px" fontSize="20px" color="teal.500">
                    Back
                </Link>
                <HStack spacing={6} alignItems="center" minWidth="20px">
                    <Button 
                        onClick={() => {
                            setShowUserData(!showUserData);
                            setShowUpdate(false);
                            handleGetUser();

                        }}
                        textAlign="left" 
                        colorScheme={showUserData ? 'red' : 'teal'}
                        minWidth="200px"            
                    >
                        Self Info
                        {/* {showUserData ? "Hide Info" : "Self Info"} */}
                    </Button>
                    <Button 
                        onClick={()=> {
                            setShowUpdate(!showUpdate);
                            setShowUserData(false);
                        }} 
                        ml={4}
                        colorScheme={showUpdate ? 'red' : 'teal'}
                        minWidth="200px"
                    >
                        Update data
                        {/* {showUpdate ? "Hide Update" : "Update data"} */}
                    </Button>
                </HStack>
                <Box>
                    {showUserData && (
                    <>
                        <VStack alignItems="flex-start" ml={4}>
                            <Text fontSize="18px">Username: {userData.username}</Text>
                            {/* <Text fontSize="20px">Password: {userData.password}</Text> */}
                            <Text fontSize="18px">Birthday: {userData.birthday}</Text>
                            <Text fontSize="18px">Last Login: {userData.last_login}</Text>
                            <Text fontSize="18px">Create Time: {userData.create_time}</Text>
                        </VStack>
                    </>
                    )}
                    {showUpdate && (
                    <>
                        <VStack spacing={4} >
                            <Text fontSize="22px" fontFamily="Arial, sans-serif">
                                Enter update data
                            </Text>
                            <Input                                
                                type="password"
                                placeholder="Password"
                                value={updateUserData.password}
                                variant={'outline'}
                                borderColor={'teal'}                    
                                onChange={(e) =>
                                setUpdateUserData({
                                    ...updateUserData,
                                    password: e.target.value,
                                })
                                }
                            />
                            <Input
                                type="text"
                                placeholder="Birthday (YYYY-mm-dd)"
                                value={updateUserData.birthday}
                                variant={'outline'}
                                borderColor={'teal'}    
                                onChange={(e) =>
                                setUpdateUserData({
                                    ...updateUserData,
                                    birthday: e.target.value,
                                })
                                }
                            />
                            <Button 
                                onClick={()=> {
                                    handleUpdateUser();
                                }} 
                                colorScheme="teal"
                                isDisabled={updateUserData.password === "" || updateUserData.birthday ===""}
                            >
                                Confirm
                            </Button>
                            <Text>{message}</Text>
                        </VStack>
                    </>
                    )}
                </Box>
            </VStack>
        </VStack>
    )
}

export default UserPage;