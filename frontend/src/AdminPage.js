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

function AdminPage(props){
    const token = props.token;
    const [userData, setUserData] = useState({
        username: '',
        password: '',
        birthday: '',
        last_login: '',
        create_time: '',
      });
    const [showUserData, setShowUserData] = useState(false);
    const [showAllData, setShowAllData] = useState(false);
    const [showDelete, setShowDelete] = useState(false);
    const [message, setMessage] = useState('');
    const [username, setUsername] = useState('');
    const [users, setUsers] = useState([]);

    if(!token){
        return(
            <VStack>
                <Text fontSize="24px">Please log in to access the admin page.</Text>
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

    const handleGetAllUser = async () => {
        try {
            const response = await fetch(`http://${HOSTNAME}/`,{
                method: 'GET',
                headers: {
                    Authorization: token,
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
            });
            const data = await response.json();
            setUsers(data.users);
        } 
        catch (error) {
            console.error('Error fetching users:', error);
        }
    };

    const handleDeleteUser = async () => {
        await fetch(`http://${HOSTNAME}/user/`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            Authorization: token,
        },
        body: `username=${username}`,
        })
        .then((response) => {
            if (response.ok) {
            setMessage(`${username} is deleted`);
            setUsername('');
            } else {
            setMessage('Delete failed');
            }
        })
        .catch((error) => {
            console.error(error);
        });
        setTimeout(() => {
            setMessage('');
          }, 500);
    };


    return(
        <VStack minH="80vh" alignItems="center" marginTop="100px">
            <VStack spacing={8} alignitem="center">
                <Link href='/' position="absolute" top="14px" left="14px" fontSize="20px" color="teal.500">
                    Back
                </Link>
                <HStack spacing={6} alignItems="center" minWidth="20px">
                    <Button 
                        onClick={() => {
                            setShowUserData(!showUserData);
                            setShowAllData(false);
                            setShowDelete(false);
                            handleGetUser();
                        }}
                        textAlign="left" 
                        colorScheme={showUserData ? 'red' : 'teal'}
                        minWidth="200px"
                    >
                        Admin Data
                        {/* {showUserData ? "Hide Admin Data" : "Admin Data"} */}
                    </Button>
                    <Button 
                        onClick={()=> {
                            handleGetAllUser();
                            setShowUserData(false);
                            setShowAllData(!showAllData);
                            setShowDelete(false);
                        }}
                        colorScheme={showAllData ? 'red' : 'teal'}
                        minWidth="200px"
                    >
                        User Data
                        {/* {showAllData ? "Hide User Data" : "User Data"} */}
                    </Button>
                    <Button 
                        onClick={()=> {
                            setShowUserData(false);
                            setShowAllData(false);
                            setShowDelete(!showDelete);
                            setMessage('');
                            setUsername('');
                        }} 
                        colorScheme={showDelete ? 'red' : 'teal'}
                        minWidth="200px"
                    >
                        Delete Data
                        {/* {showDelete ? "Hide Delete" : "Delete Data"} */}
                    </Button>
                </HStack>
                <Box>
                    {showUserData && (
                    <>
                        <VStack alignItems="flex-start">
                            <Text fontSize="18px">Username: {userData.username}</Text>
                            {/* <Text fontSize="20px">Password: {userData.password}</Text> */}
                            <Text fontSize="18px">Birthday: {userData.birthday}</Text>
                            <Text fontSize="18px">Last Login: {userData.last_login}</Text>
                            <Text fontSize="18px">Create Time: {userData.create_time}</Text>
                        </VStack>
                    </>
                    )}
                    {showAllData && (
                    <>
                        <VStack alignItems="flex-start" spacing={5}>
                            {/* <Text fontSize="20px">All Users:</Text> */}
                            {users.map((user, index) => (
                            <Box key={index}>
                                <Text fontSize="18px" color="blue">Username: {user.name}</Text>
                                {/* <Text>Password: {user.password}</Text> */}
                                <Text>Birthday: {user.birthday}</Text>
                                <Text>Last Login: {user.last_login}</Text>
                                <Text>Create Time: {user.create_time}</Text>
                            </Box>
                            ))}
                        </VStack>
                    </>
                    )
                    }
                    {showDelete && (
                    <VStack alignItems="flex-start">
                        <Box>
                            <Text fontSize="18px">Enter the username you want to delete</Text>
                            <Box h="10px" />
                            <Input
                                type="text"
                                placeholder="Username"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                variant={'outline'}
                                borderColor={'teal'}
                                />
                            <Box h="8px" />
                            <Button 
                                colorScheme="red"
                                isDisabled={username === ""}
                                onClick={handleDeleteUser}
                            >
                                Confirm
                            </Button>
                            <Text 
                                fontSize="8px"
                                color="red"
                                minHeight="20px"
                            >
                                {message}
                            </Text>
                        </Box>
                    </VStack>
                    )}
                </Box>
            </VStack>
        </VStack>
    )

}

export default AdminPage;