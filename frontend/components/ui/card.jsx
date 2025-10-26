import * as React from "react"
import { cn } from "@/lib/utils"

const Card = React.forwardRef(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "mx-auto my-16 flex w-full flex-col items-center justify-center rounded-[10px] bg-[#FF6B35] px-8 py-6 shadow-[0_24px_48px_-24px_rgba(255,107,53,0.55)] md:w-2/3",
      className
    )}
    {...props}
  />
))
Card.displayName = "Card"

const CardHeader = React.forwardRef(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("w-full px-8 text-center", className)}
    {...props}
  />
))
CardHeader.displayName = "CardHeader"

const CardTitle = React.forwardRef(({ className, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn(
      "text-base font-medium text-white",
      className
    )}
    {...props}
  />
))
CardTitle.displayName = "CardTitle"

const CardDescription = React.forwardRef(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn("text-sm text-white/85", className)}
    {...props}
  />
))
CardDescription.displayName = "CardDescription"

const CardContent = React.forwardRef(({ className, children, ...props }, ref) => {
  const hasChildren = React.Children.count(children) > 0
  const colorClasses = hasChildren ? "text-[#2f2a28]" : "text-white"

  return (
    <div
      ref={ref}
      className={cn(
        "flex w-full min-h-[4.5rem] items-center justify-center px-6 text-center text-base font-medium",
        colorClasses,
        className
      )}
      {...props}
    >
      {hasChildren ? children : "What's your role, interests, and skills?"}
    </div>
  )
})
CardContent.displayName = "CardContent"

const CardFooter = React.forwardRef(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex w-full items-center justify-center px-8 pt-0", className)}
    {...props}
  />
))
CardFooter.displayName = "CardFooter"

export { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent }
