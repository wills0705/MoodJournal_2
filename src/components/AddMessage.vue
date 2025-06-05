<template>
    <div>
      <h1>Add Message</h1>
      <input v-model="message" placeholder="Type a message" />
      <button @click="addMessage">Send</button>
    </div>
  </template>
  
  <script>
  import { ref } from 'vue';
  import { db, realtimedb } from '../firebase'; 
  import { push, ref as dbRef } from 'firebase/database';
  
  export default {
    setup() {
      const message = ref('');
  
      const addMessage = async () => {
        if (message.value.trim()) {
          await push(dbRef(realtimedb, 'messages'), {
            text: message.value,
            timestamp: Date.now(),
          });
          message.value = '';
        }
      };
  
      return { message, addMessage };
    },
  };
  </script>
  