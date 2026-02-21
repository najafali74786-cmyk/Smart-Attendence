// static/app.js - The Brain of NA Corp Kiosk

const video = document.getElementById('videoElement');
const markBtn = document.getElementById('markBtn');
const statusMsg = document.getElementById('statusMsg');
const ledgerList = document.getElementById('ledgerList');

// 1. Camera Start
async function startCamera() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
    } catch (err) {
        statusMsg.innerText = "Camera Error! Please allow access.";
        statusMsg.className = "mt-4 text-center font-bold text-red-500";
    }
}

// 2. Scan & Mark Attendance
markBtn.addEventListener('click', async () => {
    markBtn.disabled = true;
    markBtn.innerText = "RECOGNIZING...";
    statusMsg.innerText = "";

    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);
    const base64Image = canvas.toDataURL('image/jpeg');

    try {
        const response = await fetch('/api/recognize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image_base64: base64Image })
        });

        const result = await response.json();

        if (response.ok) {
            statusMsg.innerText = result.message;
            statusMsg.className = "mt-4 text-center font-bold text-emerald-400";
            updateLedger(result.student); 
        } else {
            statusMsg.innerText = result.detail || "Authentication Failed";
            statusMsg.className = "mt-4 text-center font-bold text-red-500";
        }
    } catch (error) {
        statusMsg.innerText = "Server/Cloud Connection Error";
        statusMsg.className = "mt-4 text-center font-bold text-red-500";
    }

    setTimeout(() => {
        markBtn.disabled = false;
        markBtn.innerText = "SCAN & MARK PRESENT";
    }, 2000);
});

// 3. Update UI Ledger
function updateLedger(student) {
    if (ledgerList.innerHTML.includes('Waiting for first scan')) ledgerList.innerHTML = '';

    const card = document.createElement('div');
    card.className = "bg-slate-700/50 p-4 rounded-2xl flex justify-between items-center border border-slate-600 shadow-md animate-bounce";
    card.innerHTML = `
        <div>
            <p class="text-white font-black text-lg">${student.name}</p>
            <p class="text-slate-400 text-xs">ID: ${student.roll_no}</p>
        </div>
        <div class="text-right">
            <span class="bg-emerald-500 text-white px-2 py-0.5 rounded text-[10px] font-black uppercase">Present</span>
            <p class="text-slate-400 text-xs mt-1 font-mono">${new Date().toLocaleTimeString()}</p>
        </div>
    `;
    ledgerList.prepend(card);
    setTimeout(() => card.classList.remove('animate-bounce'), 1000);
}

// Clock Logic
setInterval(() => {
    const now = new Date();
    document.getElementById('clock').innerText = now.toLocaleTimeString();
    document.getElementById('date').innerText = now.toDateString();
}, 1000);

startCamera();