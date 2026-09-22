import * as React from "react"
import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export const Button = React.forwardRef<HTMLButtonElement, React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: 'primary' | 'secondary' | 'danger' | 'outline' | 'ghost' }>(({ className, variant = 'primary', ...props }, ref) => {
  const baseStyles = "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-slate-400 disabled:pointer-events-none disabled:opacity-50 h-9 px-4 py-2"
  const variants = {
    primary: "bg-slate-900 dark:bg-slate-50 text-slate-50 dark:text-slate-900 shadow hover:bg-slate-900/90 dark:hover:bg-slate-200",
    secondary: "bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-slate-100 shadow-sm hover:bg-slate-200 dark:hover:bg-slate-700",
    danger: "bg-red-500 dark:bg-red-600 text-white shadow-sm hover:bg-red-500/90 dark:hover:bg-red-500",
    outline: "border border-slate-200 dark:border-slate-700 bg-transparent shadow-sm hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-900 dark:text-slate-100",
    ghost: "hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-900 dark:text-slate-100",
  }
  return <button ref={ref} className={cn(baseStyles, variants[variant], className)} {...props} />
})
Button.displayName = "Button"

export const Input = React.forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(({ className, ...props }, ref) => {
  return (
    <input
      ref={ref}
      className={cn(
        "flex h-9 w-full rounded-md border border-slate-200 dark:border-slate-700 bg-transparent px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-slate-500 dark:text-slate-400 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-slate-400 disabled:cursor-not-allowed disabled:opacity-50",
        className
      )}
      {...props}
    />
  )
})
Input.displayName = "Input"

export const Card = ({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
  <div className={cn("rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-950 dark:text-slate-50 shadow", className)} {...props} />
)
export const CardHeader = ({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
  <div className={cn("flex flex-col space-y-1.5 p-6", className)} {...props} />
)
export const CardTitle = ({ className, ...props }: React.HTMLAttributes<HTMLHeadingElement>) => (
  <h3 className={cn("font-semibold leading-none tracking-tight", className)} {...props} />
)
export const CardContent = ({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
  <div className={cn("p-6 pt-0", className)} {...props} />
)

export const Badge = ({ className, variant = 'default', ...props }: React.HTMLAttributes<HTMLDivElement> & { variant?: 'default' | 'success' | 'warning' | 'danger' }) => {
  const variants = {
    default: "bg-slate-100 dark:bg-slate-700 text-slate-900 dark:text-slate-100",
    success: "bg-emerald-100 dark:bg-emerald-900/50 text-emerald-800 dark:text-emerald-300",
    warning: "bg-amber-100 dark:bg-amber-900/50 text-amber-800 dark:text-amber-300",
    danger: "bg-red-100 dark:bg-red-900/50 text-red-800 dark:text-red-300"
  }
  return <div className={cn("inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2", variants[variant], className)} {...props} />
}
