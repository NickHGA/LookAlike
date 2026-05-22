import { useMemo, useState } from 'react';

type Match = {
  name: string;
  score: number;
  image_url: string;
  category?: string;
};

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string>('');
  const [matches, setMatches] = useState<Match[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({ totalSearches: 0, averageScore: 0 });
  const [mode, setMode] = useState<string>('human');

  const handleFile = (selected: File | null) => {
    setError(null);
    setMatches([]);
    setFile(selected);
    if (selected) {
      setPreview(URL.createObjectURL(selected));
    } else {
      setPreview('');
    }
  };

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    if (event.dataTransfer.files.length > 0) {
      handleFile(event.dataTransfer.files[0]);
    }
  };

  const handleClear = () => {
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

    const formData = new FormData();
    formData.append('file', file);
    formData.append('mode', mode);
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://127.0.0.1:8000/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const result = await response.json();
        throw new Error(result.detail || 'Erreur lors de l’envoi de l’image.');
      }

      const data = await response.json();
      setMatches(data.matches || []);
      
      // Mettre à jour les statistiques
      const newStats = {
        totalSearches: stats.totalSearches + 1,
        averageScore: data.matches && data.matches.length > 0 
          ? data.matches.reduce((sum: number, match: Match) => sum + match.score, 0) / data.matches.length
          : stats.averageScore
      };
      setStats(newStats);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur inattendue.');
    } finally {
      setLoading(false);
    }
  };

  const previewStyle = useMemo(
    () => ({
      backgroundImage: preview ? `url(${preview})` : 'none',
    }),
    [preview]
  );

  return (
    <div className="app-shell">
      <header>
        <h1>LookAlike</h1>
        <p>Envoyez une photo pour trouver vos sosies célèbres.</p>
        
        {stats.totalSearches > 0 && (
          <div className="stats-panel">
            <div className="stat-item">
              <span className="stat-label">Recherches</span>
              <span className="stat-value">{stats.totalSearches}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Score moyen</span>
              <span className="stat-value">{(stats.averageScore * 100).toFixed(1)}%</span>
            </div>
          </div>
        )}
      </header>

      <main>
        <section className="mode-selector" style={{display: 'flex', gap: '15px', justifyContent: 'center', marginBottom: '20px'}}>
          <label style={{cursor: 'pointer'}}>
            <input type="radio" name="mode" value="human" checked={mode === 'human'} onChange={(e) => setMode(e.target.value)} /> Humain Célèbre
          </label>
          <label style={{cursor: 'pointer'}}>
            <input type="radio" name="mode" value="cartoon" checked={mode === 'cartoon'} onChange={(e) => setMode(e.target.value)} /> Cartoon
          </label>
          <label style={{cursor: 'pointer'}}>
            <input type="radio" name="mode" value="anime" checked={mode === 'anime'} onChange={(e) => setMode(e.target.value)} /> Anime
          </label>
        </section>

        <section className="upload-panel">
          <div
            className="drop-zone"
            onDrop={handleDrop}
            onDragOver={(event) => event.preventDefault()}
            style={previewStyle}
          >
            {!preview ? (
              <>
                <strong>Glisser-déposer</strong>
                <span>ou cliquez pour sélectionner une image</span>
              </>
            ) : (
              <div className="preview-label">Aperçu</div>
            )}
            <input
              type="file"
              accept="image/*"
              onChange={(event) => handleFile(event.target.files?.[0] ?? null)}
            />
          </div>

          <div className="actions">
            <div className="button-group">
              <button type="button" onClick={handleUpload} disabled={loading || !file}>
                {loading ? (
                  <>
                    <span className="loading-spinner"></span>
                    Recherche en cours...
                  </>
                ) : (
                  'Trouver mon sosie'
                )}
              </button>
              {(file || matches.length > 0) && (
                <button type="button" onClick={handleClear} className="clear-button" disabled={loading}>
                  Effacer
                </button>
              )}
            </div>
            {error && <div className="error-box">{error}</div>}
          </div>
        </section>

        <section className="results-panel">
          {matches.length > 0 ? (
            <>
              <h2>Résultats</h2>
              <div className="results-grid">
                {matches.map((match) => (
                  <article key={match.name} className="result-card">
                    <img src={`http://127.0.0.1:8000${match.image_url}`} alt={match.name} />
                    <div className="result-info">
                      <span className="result-name">{match.name}</span>
                      <span className="result-score">Score : {(match.score * 100).toFixed(1)}%</span>
                      {match.category && <span className="result-category">{match.category}</span>}
                    </div>
                  </article>
                ))}
              </div>
            </>
          ) : (
            <div className="placeholder-card">
              <p>Les résultats apparaîtront ici après l'analyse.</p>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;
