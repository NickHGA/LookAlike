import { useCallback, useMemo, useState } from 'react';

type Match = {
  name: string;
  score: number;
  image_url: string;
  category?: string;
};

const MAX_UPLOAD_SIZE = 10 * 1024 * 1024; // 10 MB
const COMPRESS_MAX_DIM = 800;
const COMPRESS_QUALITY = 0.85;

function compressImage(file: File): Promise<File> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    const url = URL.createObjectURL(file);

    img.onload = () => {
      URL.revokeObjectURL(url);
      let { width, height } = img;
      if (width > COMPRESS_MAX_DIM || height > COMPRESS_MAX_DIM) {
        const ratio = Math.min(COMPRESS_MAX_DIM / width, COMPRESS_MAX_DIM / height);
        width = Math.round(width * ratio);
        height = Math.round(height * ratio);
      }
      const canvas = document.createElement('canvas');
      canvas.width = width;
      canvas.height = height;
      const ctx = canvas.getContext('2d');
      if (!ctx) return reject(new Error('Canvas error.'));
      ctx.drawImage(img, 0, 0, width, height);

      canvas.toBlob(
        (blob) => {
          if (!blob) return reject(new Error('Compression error.'));
          resolve(new File([blob], file.name.replace(/\.\w+$/, '.jpg'), { type: 'image/jpeg' }));
        },
        'image/jpeg',
        COMPRESS_QUALITY
      );
    };
    img.onerror = () => {
      URL.revokeObjectURL(url);
      reject(new Error("Erreur de lecture de l'image."));
    };
    img.src = url;
  });
}

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string>('');
  const [matches, setMatches] = useState<Match[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({ totalSearches: 0, averageScore: 0 });
  const [mode, setMode] = useState<string>('human');

  const handleFile = useCallback((selected: File | null) => {
    setError(null);
    setMatches([]);
    if (preview) URL.revokeObjectURL(preview);
    setFile(selected);
    
    if (selected) {
      if (selected.size > MAX_UPLOAD_SIZE) {
        setError(`Fichier trop lourd (${(selected.size / (1024 * 1024)).toFixed(1)} MB). Max: 10 MB.`);
        setFile(null);
        setPreview('');
        return;
      }
      setPreview(URL.createObjectURL(selected));
    } else {
      setPreview('');
    }
  }, [preview]);

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (e.dataTransfer.files.length > 0) handleFile(e.dataTransfer.files[0]);
  };

  const handleClear = () => {
    if (preview) URL.revokeObjectURL(preview);
    setFile(null);
    setPreview('');
    setMatches([]);
    setError(null);
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Veuillez sélectionner une image.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const compressed = await compressImage(file);
      const formData = new FormData();
      formData.append('file', compressed);
      formData.append('mode', mode);

      const response = await fetch('http://127.0.0.1:8000/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const result = await response.json();
        throw new Error(result.detail || "Erreur lors de l'analyse.");
      }

      const data = await response.json();
      const newMatches = data.matches || [];
      setMatches(newMatches);
      
      setStats(prev => ({
        totalSearches: prev.totalSearches + 1,
        averageScore: newMatches.length > 0 
          ? newMatches.reduce((s: number, m: Match) => s + m.score, 0) / newMatches.length
          : prev.averageScore
      }));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur inattendue.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-shell">
      <header>
        <h1>LookAlike</h1>
        <p>Découvrez votre jumeau numérique grâce à l'intelligence artificielle.</p>
        
        {stats.totalSearches > 0 && (
          <div className="stats-panel">
            <div className="stat-item">
              <span className="stat-label">Recherches</span>
              <span className="stat-value">{stats.totalSearches}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Score Moyen</span>
              <span className="stat-value">{(stats.averageScore * 100).toFixed(1)}%</span>
            </div>
          </div>
        )}
      </header>

      <main>
        <section className="mode-selector">
          {[
            { id: 'human', label: 'Humain' },
            { id: 'cartoon', label: 'Cartoon' },
            { id: 'anime', label: 'Anime' }
          ].map(m => (
            <label key={m.id} className={`mode-label ${mode === m.id ? 'active' : ''}`}>
              <input type="radio" name="mode" value={m.id} checked={mode === m.id} onChange={e => setMode(e.target.value)} />
              {m.label}
            </label>
          ))}
        </section>

        <section className="upload-panel">
          <div 
            className="drop-zone" 
            onDrop={handleDrop} 
            onDragOver={e => e.preventDefault()}
            style={{ backgroundImage: preview ? `url(${preview})` : 'none' }}
          >
            {!preview ? (
              <div className="drop-content">
                <strong>Glisser-déposer une photo</strong>
                <span>Ou cliquer pour parcourir</span>
              </div>
            ) : (
              <div className="preview-label">Aperçu de l'image</div>
            )}
            <input type="file" accept="image/*" onChange={e => handleFile(e.target.files?.[0] ?? null)} />
          </div>

          <div className="actions">
            <div className="actions-text">
              <h3>Prêt à analyser</h3>
              <p>{file ? file.name : "Aucune image sélectionnée."}</p>
            </div>
            
            <button className="primary-btn" onClick={handleUpload} disabled={loading || !file}>
              {loading && <span className="spinner"></span>}
              {loading ? 'Analyse...' : 'Trouver mon sosie'}
            </button>
            
            {(file || matches.length > 0) && (
              <button className="secondary-btn" onClick={handleClear} disabled={loading}>
                Effacer
              </button>
            )}

            {error && <div className="error-msg">{error}</div>}
          </div>
        </section>

        {matches.length > 0 && (
          <section className="results-section">
            <div className="results-header">
              <h2>Top {matches.length} Résultats</h2>
            </div>
            
            <div className="results-grid">
              {matches.map((match, index) => (
                <article key={`${match.name}-${index}`} className="result-card">
                  <div className="img-container">
                    <img src={`http://127.0.0.1:8000${match.image_url}`} alt={match.name} />
                    <span className={`match-rank ${index === 0 ? 'rank-1' : ''}`}>
                      {index === 0 ? '🥇 Match Idéal' : `#${index + 1}`}
                    </span>
                  </div>
                  <div className="result-info">
                    <h3>{match.name}</h3>
                    <div className="score-bar-bg">
                      <div 
                        className="score-bar-fill" 
                        style={{ width: `${Math.round(match.score * 100)}%` }}
                      ></div>
                    </div>
                    <div className="score-text">
                      <span>Confiance</span>
                      <strong>{(match.score * 100).toFixed(1)}%</strong>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          </section>
        )}
      </main>
    </div>
  );
}

export default App;