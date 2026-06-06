export function reducer(state, action) {
  if (action.type !== 'toggle') return state;
  return {
    ...state,
    todos: state.todos.map((todo) =>
      todo.id === action.id
        ? { id: todo.id, title: todo.title, completed: !todo.completed }
        : todo
    ),
  };
}
