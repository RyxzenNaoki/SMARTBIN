// pages/api/classify.js

import nextConnect from 'next-connect';
import multer from 'multer';
import { initializeApp, cert, getApps } from 'firebase-admin/app';
import { getFirestore } from 'firebase-admin/firestore';
import fs from 'fs';

// Firebase Admin SDK initialization
if (!getApps().length) {
  const serviceAccount = {
    type: "service_account",
    project_id: process.env.FB_PROJECT_ID,
    private_key_id: process.env.FB_PRIVATE_KEY_ID,
    private_key: process.env.FB_PRIVATE_KEY.replace(/\\n/g, '\n'),
    client_email: process.env.FB_CLIENT_EMAIL,
    client_id: process.env.FB_CLIENT_ID,
    auth_uri: "https://accounts.google.com/o/oauth2/auth",
    token_uri: "https://oauth2.googleapis.com/token",
    auth_provider_x509_cert_url: "https://www.googleapis.com/oauth2/v1/certs",
    client_x509_cert_url: process.env.FB_CLIENT_CERT_URL
  };

  initializeApp({ credential: cert(serviceAccount) });
}

const db = getFirestore();

// Konfigurasi multer
const upload = multer({ dest: '/tmp' });

// Middleware handler
const apiRoute = nextConnect({
  onError(error, req, res) {
    res.status(501).json({ error: `Error: ${error.message}` });
  },
  onNoMatch(req, res) {
    res.status(405).json({ error: `Method ${req.method} not allowed` });
  },
});

apiRoute.use(upload.single('image')); // menangani upload gambar

// Logika klasifikasi sederhana
function classifyImage(filename) {
  const name = filename.toLowerCase();
  const organikKeywords = ['daun', 'makanan', 'kulit', 'buah', 'nasi', 'sayur', 'sisa'];
  const anorganikKeywords = ['plastik', 'botol', 'logam', 'besi', 'kaca', 'styrofoam'];

  for (const keyword of organikKeywords) {
    if (name.includes(keyword)) return 'Organik';
  }
  for (const keyword of anorganikKeywords) {
    if (name.includes(keyword)) return 'Anorganik';
  }
  return 'Tidak diketahui'; // fallback jika tak cocok
}

apiRoute.post(async (req, res) => {
  const file = req.file;
  if (!file) {
    return res.status(400).json({ error: 'No file uploaded' });
  }

  const label = classifyImage(file.originalname);

  // Simpan hasil ke Firestore
  await db.collection('hasil_klasifikasi').add({
    namaFile: file.originalname,
    klasifikasi: label,
    waktu: new Date()
  });

  // Hapus file sementara
  fs.unlinkSync(file.path);

  res.status(200).json({ success: true, label });
});

export default apiRoute;
export const config = {
  api: {
    bodyParser: false, // Diperlukan untuk multer
  },
};
