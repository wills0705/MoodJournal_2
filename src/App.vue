<template>
  <div class="mood-journal-app">
    <div class="mood-journal-app-content">
      <!-- Auth -->
      <div v-if="!isAuthenticated">
        <Signup v-if="showSignup" @switch-auth="toggleAuthForm" />
        <Login v-else @switch-auth="toggleAuthForm" />
      </div>

      <!-- Main -->
      <div class="app-container" v-else>
        <div class="mood-journal-app-content-header">
          <div
            v-for="(item, index) in tabList"
            :key="index"
            :class="['tab-item', activeIndex === index ? 'active-item' : '']"
            @click="handleClick(index)"
          >
            {{ item.name }}
          </div>
          <button @click="logout" class="logout-button">Log Out</button>
        </div>

        <div class="mood-journal-app-content-content">
          <keep-alive exclude="analysis">
            <component
              :is="currentComponent"
              :journalList="journalList"
              :saveStatus="saveStatus"
              @updateJournal="handleUpdate"
            />
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
  onSnapshot,
  where
} from 'firebase/firestore';
import { getStorage, ref, uploadBytes, getDownloadURL } from "firebase/storage";
import { onAuthStateChanged, signOut } from 'firebase/auth';

export default {
  components: { Write, Journal, Analysis, Signup, Login },
  data() {
    return {
      journalList: [],
      tabList: [
        { name: 'Write new',    componentName: 'write'   },
        { name: 'Prev Journal', componentName: 'journal' },
        { name: 'Analytics',    componentName: 'analysis' },
      ],
      activeIndex: 0,
      currentComponent: 'write',
      isAuthenticated: false,
      showSignup: false,

      // 'idle' | 'saving' | 'success' | 'error'
      saveStatus: 'idle',

      // realtime sub
      _unsub: null,

      // --- sound for approval ---
      _audio: null,                  // HTMLAudioElement
      _approvalState: {},            // { [id]: boolean } last seen approval state
      _primedApprovalWatch: false    // avoid dinging on initial load
    };
  },

  created() {
    this._audio = new Audio('/sounds/notify.wav');
    this._audio.preload = 'auto';

    onAuthStateChanged(auth, (user) => {
      if (this._unsub) { this._unsub(); this._unsub = null; }
      this._approvalState = {};
      this._primedApprovalWatch = false;

      if (user) {
        this.isAuthenticated = true;
        this.startRealtime(user.uid);
      } else {
        this.isAuthenticated = false;
        this.journalList = [];
      }
    });
  },

  beforeUnmount() {
    if (this._unsub) { this._unsub(); this._unsub = null; }
  },

  methods: {
    // ---------- UI ----------
    toggleAuthForm() { this.showSignup = !this.showSignup; },
    async logout() {
      try { await signOut(auth); this.$message.success('Logged out successfully'); }
      catch (e) { console.error('Error logging out:', e); this.$message.error('Failed to log out'); }
    },
    handleClick(index) {
      this.activeIndex = index;
      this.currentComponent = this.tabList[index].componentName;
    },

    // ---------- Realtime with approval ding ----------
    startRealtime(userId) {
      const qRef = query(
        collection(db, 'journalList'),
        where('userId', '==', userId),
        orderBy('timestamp', 'desc')
      );

      this._unsub = onSnapshot(
        qRef,
        (snap) => {
          const rows = [];
          const latestMap = {};
          snap.forEach((doc) => {
            const data = { id: doc.id, ...doc.data() };
            rows.push(data);
            latestMap[doc.id] = !!data.isApproved;  // normalize to bool
          });
          this.journalList = rows;

          // First snapshot: record baseline, no ding
          if (!this._primedApprovalWatch) {
            this._approvalState = latestMap;
            this._primedApprovalWatch = true;
            return;
          }

          // Subsequent snapshots: ding on false/undefined -> true transitions
          Object.keys(latestMap).forEach((id) => {
            const prev = !!this._approvalState[id];
            const now = !!latestMap[id];
            if (!prev && now) this._ding();
          });
          this._approvalState = latestMap;
        },
        (err) => {
          console.warn('onSnapshot error:', err);
          if (String(err.code).toLowerCase().includes('failed-precondition')) {
            this.startRealtimeNoIndex(userId);
          } else {
            this.journalList = [];
          }
        }
      );
    },

    startRealtimeNoIndex(userId) {
      if (this._unsub) { this._unsub(); this._unsub = null; }
      const qRef = query(collection(db, 'journalList'), where('userId', '==', userId));
      this._unsub = onSnapshot(
        qRef,
        (snap) => {
          const rows = [];
          const latestMap = {};
          snap.forEach((doc) => {
            const data = { id: doc.id, ...doc.data() };
            rows.push(data);
            latestMap[doc.id] = !!data.isApproved;
          });
          rows.sort((a, b) => (b.timestamp || 0) - (a.timestamp || 0));
          this.journalList = rows;

          if (!this._primedApprovalWatch) {
            this._approvalState = latestMap;
            this._primedApprovalWatch = true;
            return;
          }
          Object.keys(latestMap).forEach((id) => {
            const prev = !!this._approvalState[id];
            const now = !!latestMap[id];
            if (!prev && now) this._ding();
          });
          this._approvalState = latestMap;
        },
        (err) => {
          console.error('onSnapshot fallback error:', err);
          this.journalList = [];
        }
      );
    },

    _ding() {
      if (!this._audio) return;
      try { this._audio.currentTime = 0; this._audio.play(); } catch (_) { /* ignore autoplay blocks */ }
    },

    // ---------- Save entry ----------
    async handleUpdate(obj) {
      this.saveStatus = 'saving';
      try {
        const user = auth.currentUser;
        if (!user) { this.$message?.error('You must be logged in.'); this.saveStatus = 'idle'; return; }

        obj.userId = user.uid;
        obj.userEmail = user.email;
        obj.timestamp = Date.now();
        obj.mood = 2;
        obj.sdImage = "";

        const presetMap = { 1: "line-art", 2: "comic-book", 3: "pixel-art", 4: "analog-film", 5: "neon-punk" };
        const style_preset = presetMap[obj.buttonNumber] || "digital-art";
        const prompt = `${obj.content}`;

        const response = await fetch('https://moodjournal-2-api.onrender.com/api/generate-image', {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ prompt, style_preset })
        });
        if (!response.ok) throw new Error('Failed to generate image');

        const data = await response.json();
        const imageUrlOnBackend = `https://moodjournal-2-api.onrender.com${data.image_url}`;

        const storage = getStorage();
        const storageRef = ref(storage, `generated_images/${Date.now()}.jpg`);
        const base64Response = await fetch(imageUrlOnBackend);
        const blob = await base64Response.blob();
        const snapshot = await uploadBytes(storageRef, blob);
        const downloadURL = await getDownloadURL(snapshot.ref);
        obj.sdImage = downloadURL;

        await addDoc(collection(db, 'journalList'), obj);
        this.$message?.success('Journal entry saved successfully');
        this.saveStatus = 'success';
        setTimeout(() => (this.saveStatus = 'idle'), 800);
      } catch (error) {
        console.error('Error adding document:', error);
        this.$message?.error('Failed to save journal entry');
        this.saveStatus = 'error';
        setTimeout(() => (this.saveStatus = 'idle'), 1200);
      }
    },

    // (kept for completeness; not used when realtime is on)
    async fetchJournalList() {
      try {
        const userId = auth.currentUser.uid;
        const q = query(collection(db, 'journalList'), orderBy('timestamp', 'desc'));
        const querySnapshot = await getDocs(q);
        this.journalList = querySnapshot.docs
          .map((doc) => ({ id: doc.id, ...doc.data() }))
          .filter((entry) => entry.userId === userId);
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

    .app-container { height: 100%; display: flex; flex-direction: column; }

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

    &-content { flex: auto; overflow: hidden; margin-top: 20px; }
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
