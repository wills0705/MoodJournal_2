<template>
    <div>
      <h1>User Data</h1>
      <ul>
        <li v-for="user in users" :key="user.id">{{ user.name }}</li>
      </ul>
    </div>
  </template>
  
  <script>
  import { ref, onMounted } from 'vue';
  import { db, realtimedb } from '../firebase'; 
  import { collection, getDocs } from 'firebase/firestore';
  
  export default {
    setup() {
      const users = ref([]);
  
      const fetchUsers = async () => {
        const querySnapshot = await getDocs(collection(db, 'users'));
        users.value = querySnapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
      };
  
      onMounted(() => {
        fetchUsers();
      });
  
      return { users };
    },
  };
  </script>
  