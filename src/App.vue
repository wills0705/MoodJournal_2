<template>
  <div class="mood-journal-app">
    <div class="mood-journal-app-content">
      <!-- Auth -->
      <div v-if="!isAuthenticated">
        <Signup v-if="showSignup" @switch-auth="toggleAuthForm" />
        <Login v-else @switch-auth="toggleAuthForm" />
      </div>

      <!-- Gate: show policy docs on first login -->
      <div v-else-if="showPolicyGate" class="app-container">
        <PolicyGate
          :docs="POLICY_DOCS"
          @accepted="handlePolicyCompleted"
        />
      </div>

      <!-- Main -->
      <div class="app-container" v-else>
        <div class="mood-journal-app-content-header">
          <div class="header-brand">Mindful</div>

          <div class="header-nav">
            <div
              v-for="(item, index) in tabList"
              :key="index"
              :class="['nav-item', activeIndex === index ? 'active' : '']"
              @click="handleClick(index)"
            >
              {{ item.name }}
            </div>

            <button @click="logout" class="logout-button">Log Out</button>
          </div>
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
import PolicyGate from './components/PolicyGate.vue';

import { auth, db } from './firebase';
import {
  collection,
  getDocs,
  addDoc,
  query,
  orderBy,
  onSnapshot,
  where,
  doc,
  getDoc,
  setDoc,
  serverTimestamp,
} from 'firebase/firestore';
import { getStorage, ref, uploadBytes, getDownloadURL } from "firebase/storage";
import { onAuthStateChanged, signOut } from 'firebase/auth';

export default {
  components: { Write, Journal, Analysis, Signup, Login, PolicyGate },
  data() {
    return {
      journalList: [],
      tabList: [
        { name: 'Write',       componentName: 'write'   },
        { name: 'My Journals', componentName: 'journal' },
        { name: 'Analytics',   componentName: 'analysis' },
      ],
      activeIndex: 0,
      currentComponent: 'write',
      isAuthenticated: false,
      showSignup: false,

      saveStatus: 'idle',
      _unsub: null,

      _audio: null,
      _approvalState: {},
      _primedApprovalWatch: false,

      showPolicyGate: false,
      POLICY_DOCS: [
        { title: 'List of Mental Health Services Available 1', url: '/policies/mentalhealth.pdf' },
        { title: 'Research Consent', url: '/policies/REB_Informed_Consent.pdf' }
      ],
      _currentUid: null,
    };
  },

  created() {
    this._audio = new Audio('/sounds/notify.wav');
    this._audio.preload = 'auto';

    onAuthStateChanged(auth, async (user) => {
      if (this._unsub) { this._unsub(); this._unsub = null; }
      this._approvalState = {};
      this._primedApprovalWatch = false;

      if (user) {
        this.isAuthenticated = true;
        this._currentUid = user.uid;

        const acknowledged = await this.checkPolicyAck(user.uid);
        this.showPolicyGate = !acknowledged;

        if (acknowledged) this.startRealtime(user.uid);
      } else {
        this.isAuthenticated = false;
        this._currentUid = null;
        this.journalList = [];
        this.showPolicyGate = false;
      }
    });
  },

  beforeUnmount() {
    if (this._unsub) { this._unsub(); this._unsub = null; }
  },

  methods: {
    async checkPolicyAck(uid) {
      try {
        const uref = doc(db, 'users', uid);
        const snap = await getDoc(uref);
        if (!snap.exists()) return false;
        return !!snap.data().policyAcknowledged;
      } catch (e) {
        console.warn('checkPolicyAck error:', e);
        return false;
      }
    },
    async handlePolicyCompleted() {
      try {
        const uid = this._currentUid || auth.currentUser?.uid;
        if (!uid) return;

        const uref = doc(db, 'users', uid);
        await setDoc(uref, { policyAcknowledged: true, policyAckAt: serverTimestamp() }, { merge: true });

        this.showPolicyGate = false;
        this.startRealtime(uid);
      } catch (e) {
        console.error('Failed to store policy ack:', e);
        this.$message?.error('Could not complete policy step, please try again.');
      }
    },

    toggleAuthForm() { this.showSignup = !this.showSignup; },
    async logout() {
      try { await signOut(auth); this.$message.success('Logged out successfully'); }
      catch (e) { console.error('Error logging out:', e); this.$message.error('Failed to log out'); }
    },
    handleClick(index) {
      this.activeIndex = index;
      this.currentComponent = this.tabList[index].componentName;
    },

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
            latestMap[doc.id] = !!data.isApproved;
          });
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
      try { this._audio.currentTime = 0; this._audio.play(); } catch (_) {}
    },

    async handleUpdate(obj) {
      // unchanged - leaving your existing save logic as-is
      this.saveStatus = 'saving';
      try {
        const user = auth.currentUser;
        if (!user) {
          this.$message?.error('You must be logged in.');
          this.saveStatus = 'idle';
          return;
        }

        const content = (obj.content || '').trim();
        if (!content) {
          this.$message?.warning?.('Please write your journal content first.');
          this.saveStatus = 'idle';
          return;
        }
        if (!obj.buttonNumber) {
          this.$message?.warning?.('Please choose an image style before saving.');
          this.saveStatus = 'idle';
          return;
        }

        const presetMap = {
          1: "line-art",
          2: "comic-book",
          3: "pixel-art",
          4: "analog-film",
          5: "neon-punk",
          6: "digital-art"
        };
        const style_preset = presetMap[obj.buttonNumber];
        if (!style_preset) {
          this.$message?.error('Invalid style selection. Please pick a style again.');
          this.saveStatus = 'idle';
          return;
        }

        obj.userId = user.uid;
        obj.userEmail = user.email;
        obj.timestamp = Date.now();
        obj.mood = 2;
        obj.sdImage = "";
        obj.isApproved = false;
        obj.content = content;

        const response = await fetch('https://moodjournal-2-api.onrender.com/api/generate-image', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
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
      justify-content: space-between;
      padding: 6px 4px;
      border-bottom: 1px solid #e5e7eb;
    }

    &-content { flex: auto; overflow: hidden; margin-top: 20px; }
  }
}

.header-brand {
  font-size: 18px;
  font-weight: 700;
  color: #111827;
}


.header-nav {
  display: flex;
  align-items: center;
  gap: 22px;
}

.nav-item {
  cursor: pointer;
  color: #6b7280;
  font-size: 16px;
  font-weight: 500;
}

.nav-item.active {
  color: #111827;
  font-weight: 800;
}

.logout-button {
  margin-left: 10px;
  padding: 8px 14px;
  background-color: #9e9e9e;
  color: white;
  border: none;
  border-radius: 10px;
  cursor: pointer;
}
</style>
