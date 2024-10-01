// src/components/UserProfile.js
import React, { useEffect, useState } from "react";
import { getUser } from "../api";

const UserProfile = ({ username }) => {
  const [user, setUser] = useState(null);

  useEffect(() => {
    getUser(username)
      .then((response) => {
        setUser(response.data);
      })
      .catch((error) => {
        console.error("Error fetching user:", error);
      });
  }, [username]);

  if (!user) return <div>Loading...</div>;

  return (
    <div>
      <h1>Welcome, {user.username}</h1>
      {/* Display other user information */}
    </div>
  );
};

export default UserProfile;
