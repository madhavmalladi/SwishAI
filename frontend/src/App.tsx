import { useState } from "react";
import reactLogo from "./assets/react.svg";
import viteLogo from "/vite.svg";

interface Player {
  id: number;
  name: string;
  all_star_count: number;
  image_url?: string;
}

function App() {
  const [count, setCount] = useState(0);
  const [player, setPlayer] = useState<Player | null>(null);
  const [loading, setLoading] = useState(false);
  const [imageError, setImageError] = useState(false);

  const fetchRandomPlayer = async () => {
    setLoading(true);
    setImageError(false);
    try {
      const response = await fetch("/api/generate", {
        method: "GET",
      });
      const data = await response.json();
      setPlayer(data);
    } catch (error) {
      console.error("Error fetching player:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleImageError = () => {
    setImageError(true);
  };

  const handleImageLoad = () => {
    setImageError(false);
  };

  return (
    <div className="w-full min-h-screen p-8 text-center bg-gradient-to-br from-slate-900 via-blue-900 to-slate-800">
      <header className="border-b border-slate-700/50 bg-slate-900/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-1">
          <div className="text-center">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-orange-400 to-red-500 bg-clip-text text-transparent mb-2">
              SwishAI
            </h1>
            <p className="text-slate-400">
              Guess the NBA player from their career stats!
            </p>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto mt-8">
        <button
          onClick={fetchRandomPlayer}
          disabled={loading}
          className="px-6 py-3 bg-gradient-to-r from-orange-500 to-red-600 hover:from-orange-600 hover:to-red-700 text-white font-semibold rounded-lg shadow-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? "Loading..." : "Generate Random Player"}
        </button>

        {player && (
          <div className="mt-8 p-6 bg-slate-800/50 rounded-lg border border-slate-700">
            <h2 className="text-2xl font-bold text-white mb-4">Player Data</h2>

            {/* Player Image */}
            <div className="mb-6 flex justify-center">
              <div className="relative">
                {player.image_url && !imageError ? (
                  <img
                    src={player.image_url}
                    alt={`${player.name}`}
                    className="w-48 h-48 object-cover rounded-lg shadow-lg border-2 border-slate-600"
                    onError={handleImageError}
                    onLoad={handleImageLoad}
                    crossOrigin="anonymous"
                  />
                ) : (
                  <div className="w-48 h-48 bg-slate-700 rounded-lg shadow-lg border-2 border-slate-600 flex items-center justify-center text-slate-400">
                    <div className="text-center">
                      <div className="text-6xl mb-2">🏀</div>
                      <div className="text-sm">Image not available</div>
                      <div className="text-xs mt-1">CORS restricted</div>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Player Info */}
            <div className="mb-4 text-center">
              <h3 className="text-xl font-semibold text-white mb-2">
                {player.name}
              </h3>
              <p className="text-slate-300">
                All-Star Appearances: {player.all_star_count}
              </p>
              {player.image_url && (
                <p className="text-xs text-slate-500 mt-2">
                  Image URL: {player.image_url}
                </p>
              )}
            </div>

            {/* JSON Data */}
            <pre className="text-left text-sm text-slate-300 bg-slate-900 p-4 rounded overflow-auto">
              {JSON.stringify(player, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
