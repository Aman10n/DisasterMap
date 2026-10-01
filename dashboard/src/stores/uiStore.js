import { create } from 'zustand';

let toastId = 0;

export const useUIStore = create((set) => ({
  toasts: [],
  modals: {},

  addToast: (message, type = 'info', duration = 3500) => {
    const id = ++toastId;
    set((s) => ({ toasts: [...s.toasts, { id, message, type }] }));
    setTimeout(() => {
      set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) }));
    }, duration);
  },

  openModal: (name, data = null) => set((s) => ({
    modals: { ...s.modals, [name]: { open: true, data } },
  })),

  closeModal: (name) => set((s) => ({
    modals: { ...s.modals, [name]: { open: false, data: null } },
  })),
}));
