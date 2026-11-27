'use strict';

const list = document.getElementById('habit-list');
const form = document.getElementById('habit-form');
const nameInput = document.getElementById('habit-name');
const errorBox = document.getElementById('form-error');
const emptyState = document.getElementById('empty-state');
const loading = document.getElementById('loading');

document.getElementById('today-label').textContent = new Date().toLocaleDateString('en-PH', {
  timeZone: 'Asia/Manila',
  weekday: 'short',
  month: 'short',
  day: 'numeric',
});

function showError(msg) {
  errorBox.textContent = msg;
  errorBox.hidden = !msg;
}

// One place for every request: returns parsed JSON (or null for 204) and throws Error(message) otherwise.
async function api(path, options) {
  let res;
  try {
    res = await fetch(path, options);
  } catch (err) {
    throw new Error('Could not reach the server. Check your connection and try again.');
  }
  let body = null;
  if (res.status !== 204) {
    try {
      body = await res.json();
    } catch (err) {
      body = null;
    }
  }
  if (!res.ok) {
    throw new Error((body && body.error) || 'Something went wrong. Please try again.');
  }
  return body;
}

// Habit names are set with textContent, so any HTML typed in a name shows as plain text.
function renderHabit(h) {
  const li = document.createElement('li');
  li.className = h.checked_today ? 'habit done' : 'habit';
  li.dataset.id = h.id;

  const name = document.createElement('span');
  name.className = 'habit-name';
  name.textContent = h.name;

  const check = document.createElement('button');
  check.type = 'button';
  check.className = 'check';
  check.textContent = h.checked_today ? 'Done today' : 'Mark done';
  check.setAttribute('aria-pressed', String(h.checked_today));
  check.addEventListener('click', () => toggleHabit(h.id));

  const del = document.createElement('button');
  del.type = 'button';
  del.className = 'delete';
  del.textContent = 'Delete';
  del.addEventListener('click', () => deleteHabit(h.id));

  const stats = document.createElement('p');
  stats.className = 'habit-stats';
  const days = h.streak === 1 ? 'day' : 'days';
  stats.textContent =
    `Streak: ${h.streak} ${days} · This week: ${h.week.count}/${h.week.target} (${h.week.percent}%)`;

  li.append(name, check, del, stats);
  return li;
}

async function loadHabits() {
  try {
    const habits = await api('/api/habits');
    list.replaceChildren(...habits.map(renderHabit));
    emptyState.hidden = habits.length > 0;
  } catch (err) {
    showError(err.message);
  } finally {
    loading.hidden = true;
  }
}

async function addHabit(name) {
  showError('');
  try {
    await api('/api/habits', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name }),
    });
    nameInput.value = '';
    nameInput.focus();
  } catch (err) {
    showError(err.message);
    return;
  }
  await loadHabits();
}

async function toggleHabit(id) {
  showError('');
  try {
    await api(`/api/habits/${id}/toggle`, { method: 'POST' });
  } catch (err) {
    showError(err.message);
  }
  await loadHabits();
}

async function deleteHabit(id) {
  showError('');
  try {
    await api(`/api/habits/${id}`, { method: 'DELETE' });
  } catch (err) {
    showError(err.message);
  }
  await loadHabits();
}

form.addEventListener('submit', (event) => {
  event.preventDefault();
  addHabit(nameInput.value);
});

loadHabits();
