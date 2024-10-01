// src/api.js
import axios from "axios";

const API_URL = "http://localhost:5001/api"; // Adjust the port if necessary

export const getUser = (username) => {
  return axios.get(`${API_URL}/users/${username}`);
};

// Add other API functions as needed
