export function reducer(state, action) {
  if (action.type === 'edit') {
    return { text: action.text, past: [...state.past, state.text], future: state.future };
  }
  if (action.type === 'undo') {
    const previous = state.past.pop();
    return { text: previous, past: state.past, future: [state.text, ...state.future] };
  }
  if (action.type === 'redo') {
    const next = state.future.shift();
    return { text: next, past: [...state.past, state.text], future: state.future };
  }
  return { ...state };
}
