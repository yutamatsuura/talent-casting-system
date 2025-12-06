'use client';

import { PublicLayout } from '@/layouts/PublicLayout';
import { TalentCastingForm } from '@/components/diagnosis/TalentCastingForm';

export default function DiagnosisPage() {
  return (
    <PublicLayout maxWidth="lg" showHeader={false}>
      <TalentCastingForm />
    </PublicLayout>
  );
}
