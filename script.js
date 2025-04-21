// script.js
import { initializeApp } from "https://www.gstatic.com/firebasejs/11.6.0/firebase-app.js";
import { getFirestore, doc, onSnapshot } from "https://www.gstatic.com/firebasejs/11.6.0/firebase-firestore.js";

const firebaseConfig = {
    apiKey: "AIzaSyCh-323pn0rAagXRgXwslRi2LoFq6xHKNs",
    authDomain: "smartbin-b3035.firebaseapp.com",
    projectId: "smartbin-b3035",
    storageBucket: "smartbin-b3035.firebasestorage.app",
    messagingSenderId: "337743596404",
    appId: "1:337743596404:web:5ab1efe98b1a7505e5fa21",
    measurementId: "G-19PFSY4ZD4"
  };

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);
const jumlahRef = doc(db, "sampah", "counter");

onSnapshot(jumlahRef, (doc) => {
  if (doc.exists()) {
    document.getElementById("jumlahSampah").innerText = doc.data().jumlah;
  }
});
