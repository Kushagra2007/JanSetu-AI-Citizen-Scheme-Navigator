const DOC_LABELS = { aadhaar: 'Aadhaar Card', pan: 'PAN Card', bank: 'Bank Account', passport: 'Passport',
  driving_license: 'Driving License', voter_id: 'Voter ID', ration_card: 'Ration Card' };

async function loadProfile() {
  const res = await apiFetch('/api/profile');
  if (!res || !res.ok) return;
  const p = await res.json();
  ['age','gender','income','occupation','state','district','category','education','marital_status'].forEach(f => {
    const el = document.getElementById(f);
    if (el && p[f] !== null && p[f] !== undefined) el.value = p[f];
  });
  document.getElementById('disability').checked = !!p.disability;
  document.getElementById('completenessFill').style.width = `${p.completeness}%`;
  document.getElementById('completenessText').textContent = `${p.completeness}% complete`;

  const docContainer = document.getElementById('docChecklist');
  docContainer.innerHTML = Object.entries(p.documents).map(([type, info]) => `
    <label style="display:flex;align-items:center;gap:10px;padding:10px;border-radius:10px;">
      <input type="checkbox" ${info.has_document ? 'checked' : ''} onchange="updateDoc('${type}', this.checked)">
      ${DOC_LABELS[type] || type} ${info.verified ? '<span class="badge badge-green">Verified via DigiLocker</span>' : ''}
    </label>`).join('');
}

async function updateDoc(docType, hasDoc) {
  await apiFetch('/api/profile/documents', { method: 'PUT', body: JSON.stringify({ doc_type: docType, has_document: hasDoc }) });
  loadProfile();
}

document.addEventListener('DOMContentLoaded', () => {
  loadProfile();
  document.getElementById('profileForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
      age: parseInt(document.getElementById('age').value) || null,
      gender: document.getElementById('gender').value || null,
      income: parseFloat(document.getElementById('income').value) || null,
      occupation: document.getElementById('occupation').value || null,
      state: document.getElementById('state').value || null,
      district: document.getElementById('district').value || null,
      category: document.getElementById('category').value || null,
      education: document.getElementById('education').value || null,
      marital_status: document.getElementById('marital_status').value || null,
      disability: document.getElementById('disability').checked,
    };
    const res = await apiFetch('/api/profile', { method: 'PUT', body: JSON.stringify(payload) });
    if (res && res.ok) { alert('Profile updated!'); loadProfile(); }
  });
});