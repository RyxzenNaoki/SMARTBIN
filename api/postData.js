import { initializeApp, cert, getApps } from 'firebase-admin/app';
import { getFirestore } from 'firebase-admin/firestore';

// Cegah re-inisialisasi kalau sudah ada app
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

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { jumlah } = req.body;

  if (typeof jumlah !== 'number') {
    return res.status(400).json({ error: 'Invalid data' });
  }

  try {
    await db.collection('sampah').doc('counter').set({ jumlah }, { merge: true });
    res.status(200).json({ success: true, message: 'Jumlah sampah updated' });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
}
