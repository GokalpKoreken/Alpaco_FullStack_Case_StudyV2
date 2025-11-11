import { AuthPanel } from '../../../src/components/AuthPanel';

export default function SignUpPage() {
  return (
    <div style={{ display: 'grid', gap: '1.5rem' }}>
      <AuthPanel
        mode="signup"
        heading="Create your DropSpot account"
        subheading="Join waitlists and claim codes as soon as drops go live."
      />
    </div>
  );
}
