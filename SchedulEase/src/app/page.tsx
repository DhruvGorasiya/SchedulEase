import HomePage from "./homepage/page";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <main>
      <HomePage />
      {children}
    </main>
  );
}
