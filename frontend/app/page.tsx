'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    // 診断ページへ自動リダイレクト
    router.replace('/diagnosis');
  }, [router]);

  return null; // リダイレクト中は何も表示しない
}
