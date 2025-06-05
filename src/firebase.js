// Import Firebase SDK functions
import { initializeApp } from 'firebase/app';
import { getAnalytics } from 'firebase/analytics';

// Import additional services you plan to use
import { getFirestore } from 'firebase/firestore'; // For Firestore
import { getDatabase } from 'firebase/database';   // For Realtime Database
import { getAuth } from 'firebase/auth';           // For Authentication
import { getStorage } from 'firebase/storage';     // For Storage

// Your Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyBdLhjpaeKi0vlGwEm2nEWYv3SnD-jtjYg",
  authDomain: "moodtrac-65e32.firebaseapp.com",
  databaseURL: "https://moodtrac-65e32-default-rtdb.firebaseio.com",
  projectId: "moodtrac-65e32",
  storageBucket: "moodtrac-65e32.appspot.com",
  messagingSenderId: "544347141784",
  appId: "1:544347141784:web:2ab625a25e67d0321042ed",
  measurementId: "G-Y6Z7BJ90HY"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);

// Initialize Firebase services
const db = getFirestore(app);        // Firestore
const realtimedb = getDatabase(app); // Realtime Database
const auth = getAuth(app);           // Authentication
const storage = getStorage(app);     // Storage

// Export the initialized services
export { app, analytics, db, realtimedb, auth, storage };
