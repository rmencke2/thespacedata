import { documentDirectory, readAsStringAsync, writeAsStringAsync } from 'expo-file-system';
import React, { createContext, useContext, useEffect, useMemo, useRef, useState } from 'react';

export type AssetType = 'Instagram Post' | 'Instagram Story' | 'LinkedIn Banner' | 'Logo Variation';
export type Tone = 'Neutral' | 'Confident' | 'Friendly';

export type PreviewContext =
  | 'Instagram feed'
  | 'Instagram story'
  | 'Business card'
  | 'Website hero';

export type Variation = {
  id: string;
  label: string;
  message: string;
};

export type GeneratedAsset = {
  id: string;
  assetType: AssetType;
  message: string;
  tone: Tone;
  imageUri: string | null;
  createdAt: number;
  status: 'draft' | 'published';
  publishedAt?: number;
  lastPreviewIndex: number;
  variations: Variation[];
  selectedVariationId: string;
  previews: {
    id: string;
    context: PreviewContext;
    title: string;
  }[];
};

type Draft = {
  assetType: AssetType | null;
  message: string;
  tone: Tone;
  imageUri: string | null;
};

export type User = { id: string };

type AppState = {
  draft: Draft;
  recents: GeneratedAsset[];
  generating: boolean;
  selectedAssetId: string | null;
  hydrated: boolean;
  /** null = not signed in. Sign-up is required only at the end (e.g. download/share). */
  user: User | null;
  actions: {
    resetDraft: () => void;
    setAssetType: (t: AssetType) => void;
    setMessage: (m: string) => void;
    setTone: (t: Tone) => void;
    setImageUri: (uri: string | null) => void;
    selectAsset: (id: string) => void;
    selectVariation: (assetId: string, variationId: string) => void;
    markPublished: (assetId: string) => void;
    setLastPreviewIndex: (assetId: string, index: number) => void;
    generateFromDraft: () => Promise<GeneratedAsset>;
    signIn: () => void;
    signOut: () => void;
  };
};

const AppStateContext = createContext<AppState | null>(null);

function makeId(prefix: string) {
  return `${prefix}_${Math.random().toString(16).slice(2)}_${Date.now().toString(16)}`;
}

const PERSIST_PATH = `${documentDirectory ?? ''}influzer-state.v1.json`;

type PersistedState = {
  recents: GeneratedAsset[];
  selectedAssetId: string | null;
};

function sleep(ms: number) {
  return new Promise<void>((resolve) => {
    setTimeout(resolve, ms);
  });
}

export function AppStateProvider({ children }: { children: React.ReactNode }) {
  const [draft, setDraft] = useState<Draft>({
    assetType: null,
    message: '',
    tone: 'Neutral',
    imageUri: null,
  });
  const [recents, setRecents] = useState<GeneratedAsset[]>([]);
  const [generating, setGenerating] = useState(false);
  const [selectedAssetId, setSelectedAssetId] = useState<string | null>(null);
  const [hydrated, setHydrated] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const savingRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        if (!documentDirectory) {
          if (!cancelled) setHydrated(true);
          return;
        }

        const raw = await readAsStringAsync(PERSIST_PATH);
        const parsed = JSON.parse(raw) as PersistedState;

        const nextRecents = Array.isArray(parsed.recents) ? parsed.recents.slice(0, 5) : [];
        const nextSelected =
          typeof parsed.selectedAssetId === 'string' ? parsed.selectedAssetId : null;
        const selectedStillExists = nextSelected
          ? nextRecents.some((a) => a.id === nextSelected)
          : false;

        if (!cancelled) {
          setRecents(nextRecents);
          setSelectedAssetId(selectedStillExists ? nextSelected : nextRecents[0]?.id ?? null);
          setHydrated(true);
        }
      } catch {
        if (!cancelled) setHydrated(true);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!hydrated) return;
    if (!documentDirectory) return;

    if (savingRef.current) clearTimeout(savingRef.current);
    savingRef.current = setTimeout(() => {
      const payload: PersistedState = {
        recents: recents.slice(0, 5),
        selectedAssetId,
      };
      void writeAsStringAsync(PERSIST_PATH, JSON.stringify(payload));
    }, 250);
  }, [hydrated, recents, selectedAssetId]);

  const actions = useMemo<AppState['actions']>(() => {
    return {
      resetDraft: () =>
        setDraft({
          assetType: null,
          message: '',
          tone: 'Neutral',
          imageUri: null,
        }),
      setAssetType: (assetType) => setDraft((d) => ({ ...d, assetType })),
      setMessage: (message) => setDraft((d) => ({ ...d, message })),
      setTone: (tone) => setDraft((d) => ({ ...d, tone })),
      setImageUri: (imageUri) => setDraft((d) => ({ ...d, imageUri })),
      selectAsset: (id) => setSelectedAssetId(id),
      selectVariation: (assetId, variationId) => {
        setRecents((prev) =>
          prev.map((a) => (a.id === assetId ? { ...a, selectedVariationId: variationId } : a))
        );
      },
      markPublished: (assetId) => {
        setRecents((prev) =>
          prev.map((a) =>
            a.id === assetId ? { ...a, status: 'published', publishedAt: Date.now() } : a
          )
        );
      },
      setLastPreviewIndex: (assetId, index) => {
        setRecents((prev) =>
          prev.map((a) => (a.id === assetId ? { ...a, lastPreviewIndex: index } : a))
        );
      },
      signIn: () => setUser({ id: makeId('user') }),
      signOut: () => setUser(null),
      generateFromDraft: async () => {
        setGenerating(true);

        try {
          // Mock "premium-feel" delay (no spinner/progress bar elsewhere)
          // Fail-safe: never hang forever (bridgeless/timers edge cases).
          let delayDone = false;
          void sleep(4500).then(() => {
            if (!delayDone) console.warn('generateFromDraft: delay fallback fired');
          });
          await sleep(1800);
          delayDone = true;

          const assetType = draft.assetType ?? 'Instagram Post';
          const message = draft.message.trim();
          const tone = draft.tone;
          const imageUri = draft.imageUri;

          const base = message || 'Grand opening this Saturday';
          const variations: Variation[] = [
            {
              id: makeId('v'),
              label: 'Variation A',
              message: base,
            },
            {
              id: makeId('v'),
              label: 'Variation B',
              message: tone === 'Confident' ? `${base}. Don’t miss it.` : `Join us: ${base}.`,
            },
            {
              id: makeId('v'),
              label: 'Variation C',
              message: tone === 'Friendly' ? `You’re invited — ${base}!` : `This is happening: ${base}.`,
            },
          ];

          const asset: GeneratedAsset = {
            id: makeId('asset'),
            assetType,
            message,
            tone,
            imageUri,
            createdAt: Date.now(),
            status: 'draft',
            lastPreviewIndex: 0,
            variations,
            selectedVariationId: variations[0]!.id,
            previews: [
              { id: makeId('p'), context: 'Instagram feed', title: 'Instagram feed preview' },
              { id: makeId('p'), context: 'Instagram story', title: 'Instagram story preview' },
              { id: makeId('p'), context: 'Business card', title: 'Business card preview' },
              { id: makeId('p'), context: 'Website hero', title: 'Website hero preview' },
            ],
          };

          setRecents((prev) => [asset, ...prev].slice(0, 5));
          setSelectedAssetId(asset.id);
          return asset;
        } finally {
          setGenerating(false);
        }
      },
    };
    // draft is intentionally captured: generation uses the snapshot at trigger time
  }, [draft]);

  const value = useMemo<AppState>(
    () => ({
      draft,
      recents,
      generating,
      selectedAssetId,
      hydrated,
      user,
      actions,
    }),
    [actions, draft, generating, hydrated, recents, selectedAssetId, user]
  );

  return <AppStateContext.Provider value={value}>{children}</AppStateContext.Provider>;
}

export function useAppState() {
  const ctx = useContext(AppStateContext);
  if (!ctx) throw new Error('useAppState must be used within AppStateProvider');
  return ctx;
}

