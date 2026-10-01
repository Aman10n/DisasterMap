import React from 'react';
import { useUIStore } from '../stores/uiStore';
import { X } from 'lucide-react';

export default function ToastContainer() {
  const toasts = useUIStore((s) => s.toasts);

  if (toasts.length === 0) return null;

  return (
    <div style={{
      position: 'fixed', bottom: 24, right: 24, zIndex: 9999,
      display: 'flex', flexDirection: 'column', gap: 8, maxWidth: 400,
    }}>
      {toasts.map((t) => (
        <div key={t.id} className={`alert-banner ${t.type}`} style={{ margin: 0, boxShadow: 'var(--shadow-lg)' }}>
          <span style={{ flex: 1 }}>{t.message}</span>
          <X size={14} style={{ cursor: 'pointer', opacity: 0.6 }}
            onClick={() => useUIStore.getState().toasts = useUIStore.getState().toasts.filter(x => x.id !== t.id)} />
        </div>
      ))}
    </div>
  );
}
