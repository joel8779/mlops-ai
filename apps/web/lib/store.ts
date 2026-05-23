import { create } from "zustand";

type RecruiterState = {
  query: string;
  selectedJobId: string | null;
  setQuery: (query: string) => void;
  setSelectedJobId: (jobId: string | null) => void;
};

export const useRecruiterStore = create<RecruiterState>((set) => ({
  query: "Python backend engineers with Docker",
  selectedJobId: null,
  setQuery: (query) => set({ query }),
  setSelectedJobId: (selectedJobId) => set({ selectedJobId })
}));
