import {
  getGroups,
  createGroup,
  addMember,
  createExpense,
  parseReceipt,
} from './api.js';

const elements = {
  groupList: document.querySelector('#group-list'),
  createGroupForm: document.querySelector('#create-group-form'),
  groupNameInput: document.querySelector('#group-name'),
  groupTitle: document.querySelector('#group-title'),
  memberCount: document.querySelector('#member-count'),
  expenseCount: document.querySelector('#expense-count'),
  netTotal: document.querySelector('#net-total'),
  memberForm: document.querySelector('#member-form'),
  memberNameInput: document.querySelector('#member-name'),
  memberList: document.querySelector('#member-list'),
  balanceSummary: document.querySelector('#balance-summary'),
  expenseForm: document.querySelector('#expense-form'),
  expenseDescription: document.querySelector('#expense-description'),
  expenseTotal: document.querySelector('#expense-total'),
  expensePayer: document.querySelector('#expense-payer'),
  splitType: document.querySelector('#split-type'),
  splitRows: document.querySelector('#split-rows'),
  parseReceiptBtn: document.querySelector('#parse-receipt-btn'),
  receiptText: document.querySelector('#receipt-text'),
  expenseList: document.querySelector('#expense-list'),
  settlementList: document.querySelector('#settlement-list'),
  toast: document.querySelector('#status-toast'),
};

const state = {
  groups: [],
  selectedGroupId: null,
  toastTimer: null,
};

const currencyFormatter = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
});

initialize();

async function initialize() {
  bindEvents();
  await loadGroups();
}

function bindEvents() {
  elements.createGroupForm.addEventListener('submit', async (event) => {
    event.preventDefault();

    const groupName = elements.groupNameInput.value.trim();

    if (!groupName) {
      showToast('Group name is required.');
      return;
    }

    try {
      console.log('[createGroup] submitting group', { groupName });
      const newGroup = await createGroup(groupName);
      console.log('[createGroup] API succeeded', newGroup);

      state.selectedGroupId = newGroup.id;
      elements.groupNameInput.value = '';

      console.log('[createGroup] reloading groups after create');
      await loadGroups();
      console.log('[createGroup] groups reloaded successfully');

      showToast(`Created group: ${newGroup.name}`);
    } catch (error) {
      console.error('[createGroup] failed', error);
      showToast(error?.message || 'Failed to add group');
    }
  });

  elements.memberForm.addEventListener('submit', async (event) => {
    event.preventDefault();

    if (!state.selectedGroupId) {
      showToast('Select or create a group first.');
      return;
    }

    const memberName = elements.memberNameInput.value.trim();

    if (!memberName) {
      showToast('Member name is required.');
      return;
    }

    try {
      await addMember(state.selectedGroupId, memberName);
      elements.memberNameInput.value = '';
      await loadGroups();
      showToast(`Added ${memberName} to the group.`);
    } catch (error) {
      showToast(error.message || 'Unable to add member.');
    }
  });

  elements.expenseForm.addEventListener('submit', async (event) => {
    event.preventDefault();

    const selectedGroup = getSelectedGroup();

    if (!selectedGroup) {
      showToast('Create or select a group first.');
      return;
    }

    if (!selectedGroup.members.length) {
      showToast('Add at least one participant before saving an expense.');
      return;
    }

    const description = elements.expenseDescription.value.trim();
    const total_amount = Number(elements.expenseTotal.value);
    const payer_id = elements.expensePayer.value;
    const splitType = elements.splitType.value;

    if (!description || !Number.isFinite(total_amount) || total_amount <= 0) {
      showToast('Please enter a valid expense description and amount.');
      return;
    }

    const splits = buildSplits(selectedGroup, total_amount, splitType);

    if (!splits) {
      return;
    }

    try {
      await createExpense(state.selectedGroupId, {
        description,
        total_amount,
        payer_id,
        splits,
      });

      elements.expenseForm.reset();
      elements.splitType.value = 'even';
      renderSplitRows(selectedGroup);
      await loadGroups();
      showToast('Expense saved successfully.');
    } catch (error) {
      showToast(error.message || 'Unable to save expense.');
    }
  });

  elements.parseReceiptBtn.addEventListener('click', async () => {
    const text = elements.receiptText.value.trim();

    if (!text) {
      showToast('Paste receipt text first.');
      return;
    }

    try {
      const parsed = await parseReceipt(text);

      elements.expenseDescription.value = parsed.description;
      elements.expenseTotal.value = parsed.total_amount > 0 ? parsed.total_amount.toFixed(2) : '';
      showToast('Receipt parsed successfully.');
    } catch (error) {
      showToast(error.message || 'Unable to parse receipt.');
    }
  });

  elements.groupList.addEventListener('click', (event) => {
    const button = event.target.closest('[data-group-id]');

    if (!button) {
      return;
    }

    state.selectedGroupId = button.dataset.groupId;
    render();
  });

  elements.splitType.addEventListener('change', () => {
    const selectedGroup = getSelectedGroup();
    renderSplitRows(selectedGroup);
  });
}

async function loadGroups() {
  try {
    state.groups = await getGroups();

    if (!state.groups.length) {
      state.selectedGroupId = null;
      render();
      return;
    }

    if (!state.selectedGroupId || !state.groups.some((group) => group.id === state.selectedGroupId)) {
      state.selectedGroupId = state.groups[0].id;
    }

    render();
  } catch (error) {
    showToast(error.message || 'Unable to load groups.');
  }
}

function render() {
  const selectedGroup = getSelectedGroup();

  renderGroupList();
  renderGroupHeader(selectedGroup);
  renderStats(selectedGroup);
  renderMembers(selectedGroup);
  renderBalanceSummary(selectedGroup);
  renderExpenseForm(selectedGroup);
  renderExpenseList(selectedGroup);
  renderSettlementList(selectedGroup);
}

function renderGroupList() {
  if (!state.groups.length) {
    elements.groupList.innerHTML = '<div class="empty-state">No groups yet. Create one to get started.</div>';
    return;
  }

  elements.groupList.innerHTML = state.groups
    .map((group) => {
      const isActive = group.id === state.selectedGroupId;
      return `
        <button class="group-item ${isActive ? 'active' : ''}" type="button" data-group-id="${group.id}">
          <span>
            <strong>${escapeHtml(group.name)}</strong>
          </span>
          <small>${group.members.length} members</small>
        </button>
      `;
    })
    .join('');
}

function renderGroupHeader(selectedGroup) {
  elements.groupTitle.textContent = selectedGroup ? selectedGroup.name : 'No group selected';
}

function renderStats(selectedGroup) {
  if (!selectedGroup) {
    elements.memberCount.textContent = '0';
    elements.expenseCount.textContent = '0';
    elements.netTotal.textContent = formatCurrency(0);
    return;
  }

  const balances = computeNetBalances(selectedGroup);
  const totalNet = balances.reduce((sum, member) => sum + member.net, 0);

  elements.memberCount.textContent = String(selectedGroup.members.length);
  elements.expenseCount.textContent = String(selectedGroup.expenses.length);
  elements.netTotal.textContent = formatCurrency(totalNet);
}

function renderMembers(selectedGroup) {
  if (!selectedGroup) {
    elements.memberList.innerHTML = '<li class="empty-state">No members added yet.</li>';
    return;
  }

  if (!selectedGroup.members.length) {
    elements.memberList.innerHTML = '<li class="empty-state">No participants yet.</li>';
    return;
  }

  elements.memberList.innerHTML = selectedGroup.members
    .map(
      (member) => `
        <li>
          <span>${escapeHtml(member.name)}</span>
          <span class="member-meta">${member.id.slice(-4)}</span>
        </li>
      `,
    )
    .join('');
}

function renderBalanceSummary(selectedGroup) {
  if (!selectedGroup) {
    elements.balanceSummary.innerHTML = '<div class="empty-state">Select a group to view balances.</div>';
    return;
  }

  const balances = computeNetBalances(selectedGroup);

  if (!balances.length) {
    elements.balanceSummary.innerHTML = '<div class="empty-state">No balances available.</div>';
    return;
  }

  elements.balanceSummary.innerHTML = balances
    .map((member) => {
      const tagClass = member.net > 0 ? 'positive' : member.net < 0 ? 'negative' : 'neutral';
      const label = member.net > 0 ? 'Should receive' : member.net < 0 ? 'Owes' : 'Settled';

      return `
        <div class="balance-row">
          <strong>${escapeHtml(member.name)}</strong>
          <span class="tag ${tagClass}">${label} ${formatCurrency(Math.abs(member.net))}</span>
        </div>
      `;
    })
    .join('');
}

function renderExpenseForm(selectedGroup) {
  elements.expenseDescription.disabled = !selectedGroup;
  elements.expenseTotal.disabled = !selectedGroup;
  elements.expensePayer.disabled = !selectedGroup;
  elements.splitType.disabled = !selectedGroup || !selectedGroup.members.length;

  if (!selectedGroup || !selectedGroup.members.length) {
    elements.expensePayer.innerHTML = '<option value="">No members</option>';
    elements.splitRows.innerHTML = '<div class="empty-state">Add members first.</div>';
    return;
  }

  const payerOptions = selectedGroup.members
    .map((member) => `<option value="${member.id}">${escapeHtml(member.name)}</option>`)
    .join('');

  elements.expensePayer.innerHTML = payerOptions;

  if (selectedGroup.members.length) {
    elements.expensePayer.value = selectedGroup.members[0].id;
  }

  elements.splitType.value = 'even';
  renderSplitRows(selectedGroup);
}

function renderSplitRows(selectedGroup) {
  if (!selectedGroup || !selectedGroup.members.length) {
    elements.splitRows.innerHTML = '<div class="empty-state">Add members to configure split rules.</div>';
    return;
  }

  const splitType = elements.splitType.value;

  if (splitType === 'even') {
    elements.splitRows.innerHTML = `
      <div class="empty-state">
        The total will be divided evenly across ${selectedGroup.members.length} participants.
      </div>
    `;
    return;
  }

  if (splitType === 'customPercentages') {
    elements.splitRows.innerHTML = selectedGroup.members
      .map(
        (member) => `
          <label class="split-row">
            <span>${escapeHtml(member.name)}</span>
            <div class="split-input">
              <input type="number" min="0" max="100" step="0.01" data-member-id="${member.id}" placeholder="0" />
              <span>%</span>
            </div>
          </label>
        `,
      )
      .join('');
    return;
  }

  elements.splitRows.innerHTML = selectedGroup.members
    .map(
      (member) => `
        <label class="split-row">
          <span>${escapeHtml(member.name)}</span>
          <div class="split-input">
            <input type="number" min="0" step="0.01" data-member-id="${member.id}" placeholder="0.00" />
            <span>$</span>
          </div>
        </label>
      `,
    )
    .join('');
}

function renderExpenseList(selectedGroup) {
  if (!selectedGroup) {
    elements.expenseList.innerHTML = '<div class="empty-state">No expenses yet.</div>';
    return;
  }

  if (!selectedGroup.expenses.length) {
    elements.expenseList.innerHTML = '<div class="empty-state">No expenses recorded yet.</div>';
    return;
  }

  elements.expenseList.innerHTML = selectedGroup.expenses
    .map((expense) => {
      const payer = selectedGroup.members.find((member) => member.id === expense.payer_id);
      const splits = expense.splits
        .map((split) => {
          const member = selectedGroup.members.find((member) => member.id === split.member_id);
          return `<span class="split-pill">${escapeHtml(member ? member.name : 'Unknown')}: ${formatCurrency(split.amount)}</span>`;
        })
        .join('');

      return `
        <article class="expense-item">
          <header>
            <h4>${escapeHtml(expense.description)}</h4>
            <span class="amount">${formatCurrency(expense.total_amount)}</span>
          </header>
          <div class="meta">Paid by ${escapeHtml(payer ? payer.name : 'Unknown')}</div>
          <div class="split-breakdown">${splits}</div>
        </article>
      `;
    })
    .join('');
}

function renderSettlementList(selectedGroup) {
  if (!selectedGroup) {
    elements.settlementList.innerHTML = '<div class="empty-state">No settlements to show.</div>';
    return;
  }

  const settlements = generateSettlements(selectedGroup);

  if (!settlements.length) {
    elements.settlementList.innerHTML = '<div class="empty-state">Everyone is settled up.</div>';
    return;
  }

  elements.settlementList.innerHTML = settlements
    .map(
      (settlement) => `
        <div class="settlement-item">
          <div>
            <strong>${escapeHtml(settlement.from)}</strong>
            <div class="meta">pays ${escapeHtml(settlement.to)}</div>
          </div>
          <span class="amount">${formatCurrency(settlement.amount)}</span>
        </div>
      `,
    )
    .join('');
}

function buildSplits(selectedGroup, totalAmount, splitType) {
  const members = selectedGroup.members;

  if (splitType === 'even') {
    const evenAmount = Number((totalAmount / members.length).toFixed(2));
    return members.map((member) => ({ member_id: member.id, amount: evenAmount }));
  }

  if (splitType === 'customPercentages') {
    const rows = Array.from(elements.splitRows.querySelectorAll('input[data-member-id]'));
    let totalPercent = 0;

    const splits = rows.map((row) => {
      const percent = Number(row.value || 0);
      totalPercent += percent;
      return {
        member_id: row.dataset.memberId,
        percent,
      };
    });

    if (Math.abs(totalPercent - 100) > 0.01) {
      showToast('Custom percentages must total exactly 100%.');
      return null;
    }

    return splits.map((split) => ({
      member_id: split.member_id,
      amount: Number(((totalAmount * split.percent) / 100).toFixed(2)),
    }));
  }

  const rows = Array.from(elements.splitRows.querySelectorAll('input[data-member-id]'));
  const splits = rows.map((row) => ({
    member_id: row.dataset.memberId,
    amount: Number(row.value || 0),
  }));

  const totalAssigned = splits.reduce((sum, split) => sum + split.amount, 0);

  if (Math.abs(totalAssigned - totalAmount) > 0.01) {
    showToast('Custom amounts must add up to the total expense amount.');
    return null;
  }

  return splits;
}

function computeNetBalances(selectedGroup) {
  if (!selectedGroup) {
    return [];
  }

  const balances = selectedGroup.members.reduce((map, member) => {
    map[member.id] = {
      id: member.id,
      name: member.name,
      net: 0,
    };
    return map;
  }, {});

  selectedGroup.expenses.forEach((expense) => {
    balances[expense.payer_id].net += expense.total_amount;

    expense.splits.forEach((split) => {
      balances[split.member_id].net -= split.amount;
    });
  });

  return Object.values(balances).map((member) => ({
    ...member,
    net: Number(member.net.toFixed(2)),
  }));
}

function generateSettlements(selectedGroup) {
  const balances = computeNetBalances(selectedGroup);

  const creditors = balances
    .filter((member) => member.net > 0.01)
    .map((member) => ({ ...member, net: Number(member.net) }));

  const debtors = balances
    .filter((member) => member.net < -0.01)
    .map((member) => ({ ...member, net: Math.abs(Number(member.net)) }));

  const settlements = [];

  while (creditors.length && debtors.length) {
    const creditor = creditors[0];
    const debtor = debtors[0];

    if (!creditor || !debtor) {
      break;
    }

    const amount = Math.min(creditor.net, debtor.net);

    settlements.push({
      from: debtor.name,
      to: creditor.name,
      amount: Number(amount.toFixed(2)),
    });

    creditor.net = Number((creditor.net - amount).toFixed(2));
    debtor.net = Number((debtor.net - amount).toFixed(2));

    if (creditor.net <= 0.01) {
      creditors.shift();
    } else {
      creditors[0] = creditor;
    }

    if (debtor.net <= 0.01) {
      debtors.shift();
    } else {
      debtors[0] = debtor;
    }
  }

  return settlements;
}

function getSelectedGroup() {
  return state.groups.find((group) => group.id === state.selectedGroupId) || null;
}

function formatCurrency(value) {
  return currencyFormatter.format(Number(value || 0));
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function showToast(message) {
  elements.toast.textContent = message;
  elements.toast.classList.add('visible');

  clearTimeout(state.toastTimer);
  state.toastTimer = setTimeout(() => {
    elements.toast.classList.remove('visible');
  }, 2200);
}
