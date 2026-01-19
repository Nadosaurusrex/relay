import { lazy, Suspense } from 'react';

const MonacoEditor = lazy(() => import('@monaco-editor/react'));

interface LazyCodeEditorProps {
  height?: string;
  defaultLanguage?: string;
  value: string;
  onChange?: (value: string | undefined) => void;
  theme?: string;
  options?: any;
}

export function LazyCodeEditor(props: LazyCodeEditorProps) {
  return (
    <Suspense
      fallback={
        <div
          className="flex items-center justify-center bg-black/40 rounded-lg border border-white/10"
          style={{ height: props.height || '400px' }}
        >
          <div className="text-muted/60">Loading editor...</div>
        </div>
      }
    >
      <MonacoEditor {...props} />
    </Suspense>
  );
}
