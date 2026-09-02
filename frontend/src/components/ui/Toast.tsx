import { createPortal } from 'react-dom';
import { useState, useCallback, useEffect, useRef } from 'react';

type ToastType = 'success' | 'error' | 'info' | 'warning';

interface ToastItem {
  id: number;
  message: string;
  type: ToastType;
}

const typeStyles: Record<ToastType, string> = {
  success: 'bg-emerald/15 border-emerald/30 text-emerald-300',
  error: 'bg-rose/15 border-rose/30 text-rose-300',
  info: 'bg-amber/15 border-amber/30 text-amber-300',
  warning: 'bg-yellow-500/15 border-yellow-500/30 text-yellow-300',
};

const typeIcons: Record<ToastType, string> = {
  success: 'fa-circle-check',
  error: 'fa-circle-xmark',
  info: 'fa-circle-info',
  warning: 'fa-triangle-exclamation',
};

// Singleton para toasts globales
let addToastGlobal: ((message: string, type?: ToastType) => void) | null = null;

export function toast(message: string, type: ToastType = 'info') {
  addToastGlobal?.(message, type);
}

export function ToastContainer() {
  const [toasts, setToasts] = useState<ToastItem[]>([]);
  const counterRef = useRef(0);

  const addToast = useCallback((message: string, type: ToastType = 'info') => {
    const id = ++counterRef.current;
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
  }, []);

  useEffect(() => {
    addToastGlobal = addToast;
    return () => { addToastGlobal = null; };
  }, [addToast]);

  return createPortal(
    <div className="fixed top-4 right-4 z-[60] flex flex-col gap-2">
      {toasts.map((t) => (
        <div
          key={t.id}
          className={`flex items-center gap-2.5 px-4 py-3 rounded-xl border text-sm font-medium animate-fade-in ${typeStyles[t.type]}`}
        >
          <i className={`fa-solid ${typeIcons[t.type]}`} />
          <span>{t.message}</span>
        </div>
      ))}
    </div>,
    document.body,
  );
}