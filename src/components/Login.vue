<template>
    <div class="auth-container">
      <h1>Log In</h1>
      <form @submit.prevent="login">
        <input v-model="email" placeholder="Email" type="email" required />
        <input v-model="password" placeholder="Password" type="password" required />
        <button type="submit">Log In</button>
        <p v-if="error" class="error">{{ error }}</p>
      </form>
      <p>
        Don't have an account?
        <button @click="$emit('switch-auth')">Sign Up</button>
      </p>
    </div>
  </template>
  
  <script>
  import { ref } from 'vue';
  import { auth } from '../firebase'; // Adjust the path as needed
  import { signInWithEmailAndPassword } from 'firebase/auth';
  
  export default {
    setup(props, { emit }) {
      const email = ref('');
      const password = ref('');
      const error = ref('');
  
      const login = async () => {
        try {
          await signInWithEmailAndPassword(auth, email.value, password.value);
          // User is signed in
        } catch (err) {
          error.value = err.message;
        }
      };
  
      return { email, password, login, error };
    },
  };
  </script>
  
  <style scoped>
  .auth-container {
    max-width: 400px;
    margin: 50px auto;
    padding: 30px 40px;
    background-color: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  }
  
  .auth-container h1 {
    text-align: center;
    margin-bottom: 30px;
    font-size: 24px;
    color: #333333;
  }
  
  .auth-container form {
    display: flex;
    flex-direction: column;
  }
  
  .auth-container input {
    padding: 12px 15px;
    margin-bottom: 20px;
    border: 1px solid #cccccc;
    border-radius: 4px;
    font-size: 16px;
  }
  
  .auth-container input:focus {
    border-color: #66afe9;
    outline: none;
  }
  
  .auth-container button[type="submit"] {
    padding: 12px 15px;
    background-color: #969696;
    color: #ffffff;
    border: none;
    border-radius: 4px;
    font-size: 16px;
    cursor: pointer;
  }
  
  .auth-container button[type="submit"]:hover {
    background-color: #454545;
  }
  
  .auth-container button {
    background: none;
    border: none;
    color: #007BFF;
    padding: 0;
    font-size: 16px;
    cursor: pointer;
  }
  
  .auth-container button:hover {
    text-decoration: underline;
  }
  
  .auth-container p {
    text-align: center;
    margin-top: 20px;
  }
  
  .auth-container .error {
    color: red;
    margin-bottom: 15px;
    text-align: center;
  }
  </style>
  