import axios from 'axios';

const API_BASE_URL = 'https://ctflife-demo.zeabur.app';

const instance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

export function setAuthToken(token: string) {
  instance.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  console.log('Auth token set for API requests');
}

export const fetchData = async (endpoint: string) => {
  try {
    const response = await instance.get(endpoint);
    return response.data;
  } catch (error) {
    console.error('Error fetching data: ', error);
    // Handle errors here or throw them to be handled where the function is called
    throw error;
  }
};