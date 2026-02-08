import type { AssetType, Tone } from '@/src/state/app-state';

function extractKeywordFromUri(uri: string) {
  try {
    const last = uri.split('/').pop() ?? '';
    const name = last.replace(/\.(png|jpg|jpeg|heic|webp)$/i, '');
    const cleaned = name.replace(/[_-]+/g, ' ').trim();
    // Ignore common camera roll names
    if (!cleaned) return null;
    if (/^img\s*\d+$/i.test(cleaned)) return null;
    if (/^dsc\s*\d+$/i.test(cleaned)) return null;
    if (/^\d{4}-\d{2}-\d{2}/.test(cleaned)) return null;
    const short = cleaned.slice(0, 32).trim();
    return short.length >= 3 ? short : null;
  } catch {
    return null;
  }
}

export function suggestTextFromImage(params: {
  assetType: AssetType | null;
  tone: Tone;
  imageUri: string;
}) {
  const { assetType, tone, imageUri } = params;
  const keyword = extractKeywordFromUri(imageUri);

  const base: string[] = [];
  if (keyword) {
    base.push(`${keyword}.`);
    base.push(`A little ${keyword.toLowerCase()} moment.`);
  }

  if (assetType === 'Instagram Story') {
    base.push('A moment worth sharing.');
    base.push('Today, in one frame.');
  } else if (assetType === 'LinkedIn Banner') {
    base.push('A small update from the work in progress.');
    base.push('Building steadily. Shipping thoughtfully.');
  } else {
    base.push('A small moment worth noticing.');
    base.push('New week. Same taste.');
  }

  const toneAdjusted = base.map((s) => {
    switch (tone) {
      case 'Confident':
        return s.replace(/\.$/, '!').replace(/^A small /, 'A bold ');
      case 'Friendly':
        return s.replace(/^New week\./, 'New week—').replace(/\.$/, '.');
      case 'Neutral':
      default:
        return s;
    }
  });

  // De-dupe and return top 3
  const out: string[] = [];
  for (const s of toneAdjusted) {
    const norm = s.trim();
    if (!norm) continue;
    if (out.includes(norm)) continue;
    out.push(norm);
    if (out.length >= 3) break;
  }
  return out;
}

