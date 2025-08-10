<template>
  <div class="mood-journal-app">
    <div class="mood-journal-app-content">
      <!-- Authentication Components -->
      <div v-if="!isAuthenticated">
        <Signup v-if="showSignup" @switch-auth="toggleAuthForm" />
        <Login v-else @switch-auth="toggleAuthForm" />
      </div>

      <!-- Main App Components -->
      <div class="app-container" v-else>
        <div class="mood-journal-app-content-header">
          <div :class="['tab-item', activeIndex === index ? 'active-item' : '']" v-for="(item, index) in tabList"
            :key="index" @click="handleClick(index)">
            {{ item.name }}
          </div>
          <!-- Logout Button -->
          <button @click="logout" class="logout-button">Log Out</button>
        </div>
        <div class="mood-journal-app-content-content">
          <keep-alive exclude="analysis">
            <component :is="currentComponent" :journalList="journalList" @updateJournal="handleUpdate">
            </component>
          </keep-alive>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Write from './views/Write';
import Journal from './views/Journal';
import Analysis from './views/Analysis';

import Signup from './components/Signup.vue';
import Login from './components/Login.vue';

import { auth, db } from './firebase';
import {
  collection,
  getDocs,
  addDoc,
  query,
  orderBy,
} from 'firebase/firestore';
import { 
  getStorage, 
  ref, 
  uploadBytes, 
  getDownloadURL 
} from "firebase/storage";
import { onAuthStateChanged, signOut } from 'firebase/auth';

export default {
  components: {
    Write,
    Journal,
    Analysis,
    Signup,
    Login,
  },
  data() {
    return {
      journalList: [
        
      ],
      tabList: [
        {
          name: 'Write new',
          componentName: 'write',
        },
        {
          name: 'Prev Journal',
          componentName: 'journal',
        },
        {
          name: 'Analytics',
          componentName: 'analysis',
        },
      ],
      activeIndex: 0,
      currentComponent: 'write',
      isAuthenticated: false,
      showSignup: false,
    };
  },
  created() {
    // Monitor authentication state
     onAuthStateChanged(auth, (user) => {
       if (user) {
         this.isAuthenticated = true;
         this.fetchJournalList();
       } else {
         this.isAuthenticated = false;
         this.journalList = [];
       }
     });
  },
  methods: {
    toggleAuthForm() {
      this.showSignup = !this.showSignup;
    },
    async logout() {
      try {
        await signOut(auth);
        this.$message.success('Logged out successfully');
      } catch (error) {
        console.error('Error logging out:', error);
        this.$message.error('Failed to log out');
      }
    },
    handleClick(index) {
      this.activeIndex = index;
      this.currentComponent = this.tabList[index].componentName;
    },

    async handleUpdate(obj) {
      try {
        console.log("[1] handleUpdate triggered with content:", obj.content);
        // Add user and timestamp metadata
        const userId = auth.currentUser.uid;
        obj.userId = userId;
        obj.timestamp = Date.now();
        obj.mood = 2; 
        obj.sdImage = "";

        const styleMap = {
          1: "in pencil sketch style",
          2: "in watercolor painting style",
          3: "in pixel art style",
          4: "in oil painting style",
          5: "in cyberpunk neon style"
        };

        const styleText = styleMap[obj.buttonNumber] || "in default illustration style";
        const prompt = `${obj.content}. Please generate this ${styleText}.`;

        const response = await fetch('https://moodjournal-2.onrender.com/api/generate-image', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ prompt }),
        });

        if (!response.ok) {
          throw new Error('Failed to generate image');
        }

        const data = await response.json();
        console.log("[4] Received image_url from Flask:", data.image_url);
        
        const imageUrlOnBackend = `https://moodjournal-2.onrender.com${data.image_url}`;
        console.log("[4.1] Full backend image URL:", imageUrlOnBackend);

        // 新增：上传到Firebase Storage
        const storage = getStorage();
        const storageRef = ref(storage, `generated_images/${Date.now()}.jpg`);
        console.log("[5] Fetching image blob from:", imageUrlOnBackend);

        // 将base64转换为Blob
        const base64Response = await fetch(imageUrlOnBackend);
        const blob = await base64Response.blob();
        console.log("[5.1] Blob content type:", blob.type);

        // 上传文件
        console.log("[6] Uploading blob to Firebase Storage...");
        const snapshot = await uploadBytes(storageRef, blob);
        const downloadURL = await getDownloadURL(snapshot.ref);
        console.log("[7] Uploaded image URL from Firebase:", downloadURL);



        const imageUrl = downloadURL; // Extract the image URL from the response

        // Add the generated image URL to the journal object under the 'sdImage' field
        obj.sdImage = imageUrl;

        // Save the updated journal entry (with image) to Firestore
        console.log("[8] Saving final journal to Firestore...");
        const docRef = await addDoc(collection(db, 'journalList'), obj);
        obj.id = docRef.id;

        // Add the new journal entry to the local journalList
        this.journalList.unshift(obj);
        console.log("[9] Journal successfully saved:", obj);
        // Provide feedback to the user
        this.$message.success('Journal entry saved successfully');
      } catch (error) {
        console.error('Error adding document:', error);
        this.$message.error('Failed to save journal entry');
      }
    },


    async fetchJournalList() {
      try {
        const userId = auth.currentUser.uid; // Get current user's UID
        const q = query(
          collection(db, 'journalList'),
          orderBy('timestamp', 'desc')
        );
        const querySnapshot = await getDocs(q);
        this.journalList = querySnapshot.docs
          .map((doc) => ({ id: doc.id, ...doc.data() }))
          .filter((entry) => entry.userId === userId); // Only include entries from the current user
      } catch (error) {
        console.error('Error fetching journalList:', error);
        this.journalList = [];
      }
    },
  },
};
</script>

<style lang="less" scoped>
.mood-journal-app {
  height: 100%;
  background: #fff;
  display: flex;
  justify-content: center;

  &-content {
    width: 80%;
    background: #f3f4f6;
    height: 100%;
    padding: 20px;
    display: flex;
    flex-direction: column;

    .app-container {
      height: 100%;
      display: flex;
      flex-direction: column;
    }

    &-header {
      flex: none;
      display: flex;
      align-items: center;
      justify-content: space-around;

      .tab-item {
        padding: 4px 20px;
        border-radius: 12px;
        transition: font-size 0.1s ease;
        cursor: pointer;
      }

      .active-item {
        font-size: 18px;
        font-weight: bold;
        color: green;
        background-color: #99CC99;
      }
    }

    &-content {
      flex: auto;
      overflow: hidden;
      margin-top: 20px;
    }
  }
}

.logout-button {
  margin-left: auto;
  padding: 4px 12px;
  background-color: #f44336;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}
</style>
