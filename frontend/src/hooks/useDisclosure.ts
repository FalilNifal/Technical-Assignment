import { useState } from "react";
export const useDisclosure = (initial = false) => {
  const [opened, setOpened] = useState(initial);
  return { opened, open: () => setOpened(true), close: () => setOpened(false) };
};
