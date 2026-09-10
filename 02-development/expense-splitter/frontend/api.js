function resolveApiBaseUrl() {
  if (typeof window === 'undefined') {
    return 'http://localhost:8000';
  }

  const { protocol, hostname } = window.location;

  if (hostname.endsWith('.app.github.dev')) {
    const forwardedHost = hostname.replace(
      /-4173(?=\.app\.github\.dev$)/,
      '-8000'
    );

    return `${protocol}//${forwardedHost}`;
  }

  return 'http://localhost:8000';
}

const API_BASE_URL = resolveApiBaseUrl();
console.log('[API] Base URL:', API_BASE_URL);

async function requestJson(path, options = {}) {
  const headers = new Headers(options.headers || {});

  if (options.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  if (!headers.has('Accept')) {
    headers.set('Accept', 'application/json');
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  const contentType = response.headers.get('content-type') || '';
  const payload = contentType.includes('application/json') ? await response.json() : await response.text();

  if (!response.ok) {
    const errorMessage =
      payload?.detail || payload?.message || payload?.error || response.statusText || 'Request failed.';
    throw new Error(errorMessage);
  }

  return payload;
}

export async function getGroups() {
  return requestJson('/api/groups');
}

export async function createGroup(name) {
  const trimmedName = name.trim();

  if (!trimmedName) {
    throw new Error('Group name is required.');
  }

  return requestJson('/api/groups', {
    method: 'POST',
    body: JSON.stringify({ name: trimmedName }),
  });
}

export async function addMember(groupId, memberName) {
  const trimmedName = memberName.trim();

  if (!trimmedName) {
    throw new Error('Member name is required.');
  }

  return requestJson(`/api/groups/${groupId}/members`, {
    method: 'POST',
    body: JSON.stringify({ name: trimmedName }),
  });
}

export async function createExpense(groupId, expensePayload) {
  return requestJson(`/api/groups/${groupId}/expenses`, {
    method: 'POST',
    body: JSON.stringify(expensePayload),
  });
}

export async function parseReceipt(receiptText) {
  const trimmedText = receiptText.trim();

  if (!trimmedText) {
    throw new Error('Paste a receipt text first.');
  }

  return requestJson('/api/ai/parse-receipt', {
    method: 'POST',
    body: JSON.stringify({ receipt_text: trimmedText }),
  });
}
