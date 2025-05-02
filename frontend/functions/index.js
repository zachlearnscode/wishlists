const functions = require('firebase-functions/v1');
const fetch = require('node-fetch')

exports.createUserInBackend = functions.auth.user().onCreate(async (user) => {
  try {
    const response = await fetch(`http://127.0.0.1:8000/users`, {
      method: 'POST',
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: user.email,
        firebase_uid: user.uid,
        name: user.email.split('@')[0] // TODO: get the user's actual display name
        // TODO: pull created timestamp off of user object
      })
    })

    console.log('Successfully created user in backend:', response.data);
  } catch (error) {
    console.error('Failed to create user in backend:', error.response?.data || error.message);
  }
});

