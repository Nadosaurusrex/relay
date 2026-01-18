import * as React from "react"
import { cn } from "../../lib/utils"

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "default" | "ghost"
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "default", ...props }, ref) => {
    return (
      <button
        className={cn(
          "px-6 py-3 font-mono text-sm transition-colors",
          "focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-white",
          "disabled:pointer-events-none disabled:opacity-50",

          variant === "default" && [
            "bg-white text-black hover:bg-gray-200"
          ],
          variant === "ghost" && [
            "text-white hover:text-gray-300"
          ],

          className
        )}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"

export { Button }
