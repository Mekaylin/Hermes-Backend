import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';
import { getStorage } from 'firebase/storage';
import config from './index';

// Initialize Firebase (only if not in mock mode)
let app: any = null;
let auth: any = null;
let db: any = null;
let storage: any = null;

if (!config.mockMode && config.firebase.apiKey) {
  try {
    app = initializeApp(config.firebase);
    auth = getAuth(app);
    db = getFirestore(app);
    storage = getStorage(app);
    
    if (config.debug) {
      console.log('Firebase initialized successfully');
    }
  } catch (error) {
    console.error('Firebase initialization failed:', error);
    console.warn('Falling back to mock mode');
  }
}

// Mock implementations for development
const mockAuth = {
  currentUser: null,
  onAuthStateChanged: (callback: (user: any) => void) => {
    // Simulate logged out state
    setTimeout(() => callback(null), 100);
    return () => {}; // unsubscribe function
  },
  signInWithEmailAndPassword: async (email: string, _password: string) => {
    return { user: { uid: 'mock-user', email } };
  },
  createUserWithEmailAndPassword: async (email: string, _password: string) => {
    return { user: { uid: 'mock-user', email } };
  },
  signOut: async () => {},
  sendPasswordResetEmail: async (_email: string) => {},
};

const mockDb = {
  collection: () => ({
    doc: () => ({
      get: async () => ({ exists: () => false, data: () => null }),
      set: async () => {},
      update: async () => {},
      delete: async () => {},
    }),
    add: async () => ({ id: 'mock-doc-id' }),
    where: () => ({
      get: async () => ({ docs: [] }),
    }),
  }),
};

const mockStorage = {
  ref: () => ({
    put: async () => ({ ref: { getDownloadURL: async () => 'mock-url' } }),
    delete: async () => {},
  }),
};

export const firebaseAuth = auth || mockAuth;
export const firebaseDb = db || mockDb;
export const firebaseStorage = storage || mockStorage;
