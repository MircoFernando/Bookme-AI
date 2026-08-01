const LOGO_SRC = "/images/bookme-ai-logo.png";

const sizeClasses = {
  xs: "h-4 w-6",
  sm: "h-6 w-9",
  md: "h-9 w-12",
  lg: "h-14 w-20",
  xl: "h-20 w-28",
  hero: "h-24 w-36 sm:h-28 sm:w-40",
} as const;

export type BookMeLogoSize = keyof typeof sizeClasses;

export function BookMeLogo({
  size = "md",
  className = "",
}: {
  size?: BookMeLogoSize;
  className?: string;
}) {
  return (
    <img
      src={LOGO_SRC}
      alt="BookMe AI"
      className={`object-contain ${sizeClasses[size]} ${className}`}
    />
  );
}
