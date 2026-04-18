// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getStorage } from "firebase/storage";
import { FIREBASE_CONFIG } from "../../../../../../config";

// Initialize Firebase
const app = initializeApp(FIREBASE_CONFIG);
export const imageDB = getStorage(app);
