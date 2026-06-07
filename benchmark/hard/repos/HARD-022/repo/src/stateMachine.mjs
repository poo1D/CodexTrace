export function transition(state, event, details = {}) {
  const status = state.status;

  if (status === 'draft' && event === 'submit') {
    return withHistory(state, 'submitted', event, details);
  }

  if (status === 'draft' && event === 'cancel') {
    return withHistory(state, 'canceled', event, details);
  }

  if (status === 'submitted' && event === 'cancel') {
    return withHistory(state, 'canceled', event, details);
  }

  if (status === 'submitted' && event === 'approve') {
    return withHistory(state, 'approved', event, details);
  }

  if (status === 'approved' && event === 'ship') {
    return withHistory(state, 'shipped', event, details);
  }

  if (status === 'shipped' && event === 'deliver') {
    return withHistory(state, 'delivered', event, details);
  }

  return { ...state };
}

function withHistory(state, nextStatus, event, details) {
  const entry = {
    from: state.status,
    to: nextStatus,
    event,
    by: details.by ?? 'system',
  };
  if (details.reason) {
    entry.reason = details.reason;
  }
  return {
    ...state,
    status: nextStatus,
    history: [...(state.history ?? []), entry],
  };
}
