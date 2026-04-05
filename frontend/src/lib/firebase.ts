// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyBcFJ-g2cqst9G1R4PgYnwaH2wslYF0SbI",
  authDomain: "ventura-e277f.firebaseapp.com",
  projectId: "ventura-e277f",
  storageBucket: "ventura-e277f.firebasestorage.app",
  messagingSenderId: "966848821957",
  appId: "1:966848821957:web:ad21978c5a63afcca60eac",
  measurementId: "G-NSS5CENRCE"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = typeof window !== 'undefined' ? getAnalytics(app) : null;

export { app, analytics };
