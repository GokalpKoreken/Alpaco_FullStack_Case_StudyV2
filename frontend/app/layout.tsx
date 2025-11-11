import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'DropSpot',
  description: 'Limited drop waitlist and claim experience'
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <main>{children}</main>
      </body>
    </html>
  );
}
