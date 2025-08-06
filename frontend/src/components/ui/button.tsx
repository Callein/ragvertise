import * as React from 'react';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'default' | 'outline';
}

export const Button: React.FC<ButtonProps> = ({ variant = 'default', className, ...props }) => {
  const base = 'px-4 py-2 rounded text-white';
  const variants = {
    default: 'bg-blue-600 hover:bg-blue-700',
    outline: 'border border-gray-300 text-gray-700 bg-white hover:bg-gray-100',
  };

  return (
    <button
      className={`${base} ${variants[variant]} ${className ?? ''}`}
      {...props}
    />
  );
};