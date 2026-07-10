export function useLocalStorage<T>(key: string, initial: T): [T, (value: T) => void] {
  const stored = localStorage.getItem(key);
  let value = stored ? JSON.parse(stored) : initial;
  const setValue = (next: T) => { value = next; localStorage.setItem(key, JSON.stringify(next)); };
  return [value, setValue];
}
