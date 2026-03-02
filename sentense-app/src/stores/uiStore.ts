import { create } from 'zustand';
import { persist } from 'zustand/middleware';

type Theme = 'light' | 'dark' | 'system';

interface UIState {
  theme: Theme;
  effectiveTheme: 'light' | 'dark';
  sidebarOpen: boolean;
  sidebarCollapsed: boolean;
  activeModal: string | null;
  modalData: Record<string, unknown> | null;

  // Actions
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  toggleSidebarCollapsed: () => void;
  openModal: (id: string, data?: Record<string, unknown>) => void;
  closeModal: () => void;
}

const getEffectiveTheme = (theme: Theme): 'light' | 'dark' => {
  if (theme === 'system') {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }
  return theme;
};

const applyTheme = (theme: 'light' | 'dark') => {
  const root = document.documentElement;
  if (theme === 'dark') {
    root.classList.add('dark');
  } else {
    root.classList.remove('dark');
  }
};

export const useUIStore = create<UIState>()(
  persist(
    (set, get) => ({
      theme: 'system',
      effectiveTheme: 'light',
      sidebarOpen: true,
      sidebarCollapsed: false,
      activeModal: null,
      modalData: null,

      setTheme: (theme: Theme) => {
        const effectiveTheme = getEffectiveTheme(theme);
        applyTheme(effectiveTheme);
        set({ theme, effectiveTheme });
      },

      toggleTheme: () => {
        const { theme } = get();
        const newTheme = theme === 'light' ? 'dark' : 'light';
        const effectiveTheme = getEffectiveTheme(newTheme);
        applyTheme(effectiveTheme);
        set({ theme: newTheme, effectiveTheme });
      },

      toggleSidebar: () => {
        set((state) => ({ sidebarOpen: !state.sidebarOpen }));
      },

      setSidebarOpen: (open: boolean) => {
        set({ sidebarOpen: open });
      },

      toggleSidebarCollapsed: () => {
        set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed }));
      },

      openModal: (id: string, data?: Record<string, unknown>) => {
        set({ activeModal: id, modalData: data || null });
      },

      closeModal: () => {
        set({ activeModal: null, modalData: null });
      },
    }),
    {
      name: 'ui-storage',
      partialize: (state) => ({ 
        theme: state.theme,
        sidebarCollapsed: state.sidebarCollapsed,
      }),
      onRehydrateStorage: () => (state) => {
        if (state) {
          const effectiveTheme = getEffectiveTheme(state.theme);
          applyTheme(effectiveTheme);
          state.effectiveTheme = effectiveTheme;
        }
      },
    }
  )
);

// Listen for system theme changes
if (typeof window !== 'undefined') {
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    const { theme } = useUIStore.getState();
    if (theme === 'system') {
      const effectiveTheme = e.matches ? 'dark' : 'light';
      applyTheme(effectiveTheme);
      useUIStore.setState({ effectiveTheme });
    }
  });
}
