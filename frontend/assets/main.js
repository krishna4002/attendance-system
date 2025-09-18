/* assets/main.js
   Shared helpers for the frontend prototype.
   - Toasts & inline alerts
   - Camera helpers (start/stop, capture)
   - localStorage demo: users, attendance, schedules
   - Convenience functions used across pages
*/

// ---------- Toasts & inline alerts ----------
function toast(message, type='info', ttl=3500){
  let container = document.getElementById('toastContainer');
  if(!container){ container = document.createElement('div'); container.id='toastContainer'; container.style.position='fixed'; container.style.right='18px'; container.style.bottom='24px'; container.style.zIndex=10000; document.body.appendChild(container); }
  const el = document.createElement('div');
  el.className = 'p-3 rounded shadow border';
  el.style.marginBottom = '8px'; el.style.minWidth='200px';
  if(type==='success'){ el.style.background='#ecfdf5'; el.style.color='#064e3b'; el.style.border='1px solid #bbf7d0'; }
  else if(type==='error'){ el.style.background='#fff1f2'; el.style.color='#7f1d1d'; el.style.border='1px solid #fecaca'; }
  else if(type==='warn'){ el.style.background='#fffbeb'; el.style.color='#92400e'; el.style.border='1px solid #fef08a'; }
  else { el.style.background='#f8fafc'; el.style.color='#0f1724'; el.style.border='1px solid #e2e8f0'; }
  el.innerText = message;
  container.appendChild(el);
  setTimeout(()=> el.remove(), ttl);
}

function showInline(containerOrId, kind, text){
  const c = (typeof containerOrId === 'string') ? document.getElementById(containerOrId) : containerOrId;
  if(!c) return;
  const el = document.createElement('div'); el.className = 'inline-alert';
  if(kind==='success') el.classList.add('inline-success');
  else if(kind==='warn') el.classList.add('inline-warn');
  else el.classList.add('inline-error');
  el.innerText = text;
  c.prepend(el);
  setTimeout(()=> el.remove(), 5000);
}

// ---------- Camera helpers ----------
async function startCamera(videoEl){
  if(!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) throw new Error('Camera not supported');
  const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user', width: 1280, height: 720 }, audio: false });
  videoEl.srcObject = stream;
  await videoEl.play();
  return stream;
}

function stopStream(stream){
  if(!stream) return;
  stream.getTracks().forEach(t => t.stop());
}

function captureFrame(videoEl){
  return new Promise(resolve => {
    try{
      const canvas = document.createElement('canvas');
      canvas.width = videoEl.videoWidth || 1280;
      canvas.height = videoEl.videoHeight || 720;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(videoEl, 0, 0, canvas.width, canvas.height);
      canvas.toBlob(blob => resolve(blob), 'image/jpeg', 0.9);
    }catch(e){
      resolve(null);
    }
  });
}

// ---------- Demo storage (localStorage) ----------
const LS_USERS = 'gf_demo_users_v1';
const LS_ATT = 'gf_demo_attendance_v1';

// users: array of {id, name, role, images:[dataURL,...]}
function getAllUsers(){ try{ return JSON.parse(localStorage.getItem(LS_USERS) || '[]'); }catch(e){ return []; } }
function getUserById(id){ if(!id) return null; return getAllUsers().find(u => u.id.toUpperCase() === id.toUpperCase()); }
function getUsersByRole(role){ return getAllUsers().filter(u => u.role === role); }
function saveRegisteredUser(obj){ const users = getAllUsers(); users.push(obj); localStorage.setItem(LS_USERS, JSON.stringify(users)); window.dispatchEvent(new Event('storage')); }

function removeUser(id){ let users = getAllUsers(); users = users.filter(u => u.id !== id); localStorage.setItem(LS_USERS, JSON.stringify(users)); window.dispatchEvent(new Event('storage')); }
function clearDemoStorage(){ localStorage.removeItem(LS_USERS); localStorage.removeItem(LS_ATT); window.dispatchEvent(new Event('storage')); }

// attendance functions
function addAttendance(type, id, status){
  const users = getAllUsers(); const u = users.find(x => x.id === id) || { id, name: id };
  const logs = JSON.parse(localStorage.getItem(LS_ATT) || '[]');
  const d = new Date();
  const entry = { type, id, name: u.name || id, date: d.toISOString().slice(0,10), time: d.toTimeString().slice(0,8), status };
  logs.unshift(entry);
  localStorage.setItem(LS_ATT, JSON.stringify(logs));
}
function getAttendance(type, id){
  const logs = JSON.parse(localStorage.getItem(LS_ATT) || '[]');
  return logs.filter(l => l.type === type && l.id.toUpperCase() === id.toUpperCase());
}
function getAllAttendance(){ return JSON.parse(localStorage.getItem(LS_ATT) || '[]'); }
function clearAllAttendance(){ localStorage.removeItem(LS_ATT); }

// expose helpers globally (used by pages)
window.toast = toast;
window.showInline = showInline;
window.startCamera = startCamera;
window.stopStream = stopStream;
window.captureFrame = captureFrame;

window.getAllUsers = getAllUsers;
window.getUserById = getUserById;
window.getUsersByRole = getUsersByRole;
window.saveRegisteredUser = saveRegisteredUser;
window.removeUser = removeUser;
window.clearDemoStorage = clearDemoStorage;

window.addAttendance = addAttendance;
window.getAttendance = getAttendance;
window.getAllAttendance = getAllAttendance;
window.clearAllAttendance = clearAllAttendance;

// helper: blob -> dataURL
window.blobToDataURL = function(blob){
  return new Promise(resolve => {
    const fr = new FileReader();
    fr.onload = () => resolve(fr.result);
    fr.readAsDataURL(blob);
  });
};
