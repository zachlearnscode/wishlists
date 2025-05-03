const functions = require('firebase-functions/v1');
const axios = require('axios')

axios.defaults.baseURL = process.env.API_URL

exports.createUserInBackend = functions.auth.user().onCreate(async (user) => {
  console.log(user)
  try {
    const response = await axios.post("/users", {
      email: user.email,
      firebase_uid: user.uid
    })

    console.log('Successfully created user in backend:', response.data);
  } catch (error) {
    console.error('Failed to create user in backend:', error.response?.data || error.message);
  }
});

