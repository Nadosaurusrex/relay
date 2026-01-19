import * as React from 'react';

export interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {}

const Select = React.forwardRef<HTMLSelectElement, SelectProps>(
  ({ className, ...props }, ref) => {
    return (
      <select
        className={`flex h-12 w-full border border-white/10 bg-background px-4 py-2 font-mono text-sm transition-colors
          placeholder:text-muted
          focus-visible:outline-none focus-visible:border-white/30
          disabled:cursor-not-allowed disabled:opacity-50
          ${className}`}
        ref={ref}
        {...props}
      />
    );
  }
);
Select.displayName = 'Select';

export { Select };
