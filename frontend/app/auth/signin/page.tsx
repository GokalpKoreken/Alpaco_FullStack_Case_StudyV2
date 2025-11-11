import { AuthPanel } from '../../../src/components/AuthPanel';

export default function SignInPage() {
  return (
    <div style={{ display: 'grid', gap: '1.5rem' }}>
      <AuthPanel mode="signin" heading="Welcome back" subheading="Sign in to access active drops and your waitlist status." />
    </div>
  );
}
